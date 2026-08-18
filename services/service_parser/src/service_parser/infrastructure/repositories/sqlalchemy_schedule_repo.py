import datetime
import logging
from collections import defaultdict
from collections.abc import Iterable
from datetime import date
from itertools import batched
from typing import Literal, TypeVar, cast

from schedule_db_models import LessonCabinetORM, LessonORM
from sqlalchemy import and_, delete, inspect, or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncScalarResult, AsyncSession

from service_parser.application.ports import ScheduleRepository
from service_parser.domain.entities import Cabinet, DaySchedule, Group, Lesson
from service_parser.infrastructure.domain_mappers import (
    group_orm_to_domain,
    lesson_domain_in_orm,
    lesson_orm_to_domain,
)

logger = logging.getLogger(__name__)

Entity = TypeVar("Entity")


class SQLAlchemyScheduleRepository(ScheduleRepository):
    def __init__(self, session: "AsyncSession"):
        self.session = session

    async def save(
        self, schedules: Iterable["DaySchedule"], dates: date | tuple[date, date]
    ) -> dict[
        date,
        dict[
            Literal["group", "cabinet"],
            dict[Literal["new", "update", "remove"], set["Group | Cabinet"]],
        ],
    ]:
        schedules_list = list(schedules)
        logger.debug("Saving %d day schedules to database", len(schedules_list))

        _saving_result: dict[
            Literal["items", "add", "remove"],
            set[tuple[date, Group, Lesson]]
            | dict[Literal["schedule", "database"], set[tuple[date, Group, Lesson]]],
        ] = {
            "items": {"schedule": set(), "database": set()},
            "add": set(),
            "remove": set(),
        }

        for day_schedules in batched(schedules_list, 10):
            _result = await self._save_batch(day_schedules, dates)

            _saving_result["items"]["schedule"].update(
                _result.get("items", {}).get("schedule", set())
            )
            _saving_result["items"]["database"].update(
                _result.get("items", {}).get("database", set())
            )

            _saving_result["add"].update(
                cast(set[tuple[date, Group, Lesson]], _result.get("add", {}))
            )
            _saving_result["remove"].update(
                cast(set[tuple[date, Group, Lesson]], _result.get("remove", {}))
            )

        await self.session.commit()

        total_added = len(_saving_result.get("add", set()))
        total_removed = len(_saving_result.get("remove", set()))

        logger.debug(
            "Schedule save completed: %d schedules processed, %d lessons added, "
            "%d lessons removed",
            len(schedules_list),
            total_added,
            total_removed,
        )

        _lesson_items = _saving_result.get("items", {})

        changes = self._check_changes(
            _lesson_items.get("schedule", set()), _lesson_items.get("database", set())
        )

        return changes

    @staticmethod
    def _get_insert_columns(model_class):
        columns = []
        for column in inspect(model_class).columns:
            if column.primary_key and column.autoincrement:
                continue
            if column.server_default is not None:
                continue
            columns.append(column.key)
        return columns

    @staticmethod
    def _expand_dates(dates: date | tuple[date, date]) -> list[date]:
        if isinstance(dates, date):
            return [dates]
        start, end = dates
        return [
            start + datetime.timedelta(days=i) for i in range((end - start).days + 1)
        ]

    def _check_changes(
        self, lessons_schedule, lessons_database
    ) -> dict[
        date,
        dict[
            Literal["group", "cabinet"],
            dict[Literal["new", "update", "remove"], set["Group | Cabinet"]],
        ],
    ]:
        group_new = defaultdict(lambda: defaultdict(list))
        group_old = defaultdict(lambda: defaultdict(list))
        cabinet_new = defaultdict(lambda: defaultdict(list))
        cabinet_old = defaultdict(lambda: defaultdict(list))

        for _date, group, lesson in sorted(lessons_schedule, key=lambda x: x[1].index):
            group_new[_date][group].append(lesson)
            if lesson.cabinets:
                for cab in set(lesson.cabinets):
                    cabinet_new[_date][cab].append(lesson)

        for _date, group, lesson in sorted(lessons_database, key=lambda x: x[1].index):
            group_old[_date][group].append(lesson)
            if lesson.cabinets:
                for cab in set(lesson.cabinets):
                    cabinet_old[_date][cab].append(lesson)

        group_changes = self._compute_entity_changes(group_new, group_old)
        cabinet_changes = self._compute_entity_changes(cabinet_new, cabinet_old)

        all_dates = sorted(set(group_changes.keys()) | set(cabinet_changes.keys()))
        schedule_changes = {}
        for _date in all_dates:
            schedule_changes[_date] = {
                "group": group_changes.get(
                    _date, {"new": set(), "update": set(), "remove": set()}
                ),
                "cabinet": cabinet_changes.get(
                    _date, {"new": set(), "update": set(), "remove": set()}
                ),
            }

        return schedule_changes

    @staticmethod
    def _compute_entity_changes(
        new_data: dict[date, dict[Entity, list]],
        old_data: dict[date, dict[Entity, list]],
    ) -> dict[date, dict[Literal["new", "update", "remove"], set[Entity]]]:
        result = defaultdict(lambda: defaultdict(set))

        all_dates = sorted(set(new_data.keys()) | set(old_data.keys()))

        for _date in all_dates:
            entities_new = set(new_data.get(_date, {}).keys())
            entities_old = set(old_data.get(_date, {}).keys())

            new_entities = entities_new - entities_old
            removed_entities = entities_old - entities_new
            common_entities = entities_new & entities_old

            updated_entities = set()
            for entity in common_entities:
                lessons_new = new_data[_date][entity]
                lessons_old = old_data[_date][entity]
                if lessons_new != lessons_old:
                    updated_entities.add(entity)

            result[_date]["new"] = new_entities
            result[_date]["update"] = updated_entities
            result[_date]["remove"] = removed_entities

        return dict(result)

    async def _save_batch(
        self, schedules: Iterable["DaySchedule"], dates: date | tuple[date, date]
    ) -> dict[
        Literal["items", "add", "remove"],
        set[tuple[date, Group, Lesson]]
        | dict[Literal["schedule", "database"], set[tuple[date, Group, Lesson]]],
    ]:
        _to_update = await self._check_lessons_updates(schedules, dates)

        _lessons_to_add, _lessons_to_remove = (
            cast(set[tuple[date, Group, Lesson]], _to_update.get("add", set())),
            cast(set[tuple[date, Group, Lesson]], _to_update.get("remove", set())),
        )

        if _lessons_to_add or _lessons_to_remove:
            await self._update_schedule(_lessons_to_add, _lessons_to_remove)

        return _to_update

    async def _check_lessons_updates(
        self, schedules: Iterable["DaySchedule"], dates: date | tuple[date, date]
    ) -> dict[
        Literal["items", "add", "remove"],
        set[tuple[date, Group, Lesson]]
        | dict[Literal["schedule", "database"], set[tuple[date, Group, Lesson]]],
    ]:
        _dates = self._expand_dates(dates)

        stmt = select(LessonORM).where(
            LessonORM.group_index.in_(x.group.index for x in schedules),
            LessonORM.date.in_(_dates),
        )

        result: AsyncScalarResult[LessonORM] = await self.session.stream_scalars(stmt)

        lessons_database: set[tuple[date, Group, Lesson]] = {
            (
                lesson.date,
                group_orm_to_domain(lesson.group),
                lesson_orm_to_domain(lesson),
            )
            async for lesson in result
        }

        lessons_database_dates = defaultdict(lambda: defaultdict(int))

        for _date, group, _ in lessons_database:
            for _date in _dates:
                lessons_database_dates[_date][group] += 1

        lessons_schedule: set[tuple[date, Group, Lesson]] = {
            (_date, day_schedule.group, lesson)
            for _date in _dates
            for day_schedule in schedules
            if day_schedule.lessons
            for lesson in day_schedule.lessons
        }

        lessons_schedule_dates = defaultdict(lambda: defaultdict(int))

        for day_schedule in schedules:
            for _date in _dates:
                lessons_schedule_dates[_date][day_schedule.group] = len(
                    day_schedule.lessons
                )

        return {
            "items": {"schedule": lessons_schedule, "database": lessons_database},
            "add": lessons_schedule - lessons_database,
            "remove": lessons_database - lessons_schedule,
        }

    async def _update_schedule(
        self,
        lessons_to_add: Iterable[tuple[date, "Group", "Lesson"]],
        lessons_to_remove: Iterable[tuple[date, "Group", "Lesson"]],
    ) -> None:
        if lessons_to_remove:
            await self._remove_values(lessons_to_remove)

        if lessons_to_add:
            await self._insert_values(lessons_to_add)

    async def _insert_values(
        self, lessons_to_add: Iterable[tuple[date, "Group", "Lesson"]]
    ) -> None:
        insert_cols = self._get_insert_columns(LessonORM)

        values_list = []
        for _date, group, lesson in lessons_to_add:
            orm_obj = lesson_domain_in_orm(_date, group, lesson)
            row = {}
            for attr in inspect(orm_obj).mapper.column_attrs:
                key = attr.key
                if key in insert_cols:
                    row[key] = getattr(orm_obj, key)
            values_list.append(row)

        lessons_id = None

        if values_list:
            stmt = insert(LessonORM).values(values_list).returning(LessonORM.id)
            lessons_id = (await self.session.scalars(stmt)).all()

        if lessons_id is not None:
            cabinet_values_list = []
            for (_, _, lesson), lesson_id in zip(
                lessons_to_add, lessons_id, strict=False
            ):
                if lesson.cabinets:
                    for cabinet_idx, cabinet in enumerate(lesson.cabinets):
                        cabinet_values_list.append(
                            {
                                "lesson_id": lesson_id,
                                "cabinet_id": cabinet.index,
                                "cabinet_index": cabinet_idx,
                            }
                        )

            if cabinet_values_list:
                stmt = insert(LessonCabinetORM).values(cabinet_values_list)
                await self.session.execute(stmt)

    async def _remove_values(
        self, lessons_to_remove: Iterable[tuple[date, "Group", "Lesson"]]
    ) -> None:
        stmt = delete(LessonORM).where(
            or_(
                *[
                    and_(
                        LessonORM.date == _date,
                        LessonORM.group_index == group.index,
                        LessonORM.start == lesson.start,
                        LessonORM.end == lesson.end,
                        LessonORM.name == lesson.name,
                    )
                    for _date, group, lesson in lessons_to_remove
                ]
            )
        )
        await self.session.execute(stmt)
