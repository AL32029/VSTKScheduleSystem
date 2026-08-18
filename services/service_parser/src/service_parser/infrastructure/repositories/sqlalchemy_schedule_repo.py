import datetime
import logging
from collections.abc import Iterable
from datetime import date
from itertools import batched
from typing import Literal

from schedule_db_models import LessonCabinetORM, LessonORM
from sqlalchemy import and_, delete, inspect, or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncScalarResult, AsyncSession

from service_parser.application.ports import ScheduleRepository
from service_parser.domain.entities import DaySchedule, Group, Lesson
from service_parser.infrastructure.domain_mappers import (
    group_orm_to_domain,
    lesson_domain_in_orm,
    lesson_orm_to_domain,
)

logger = logging.getLogger(__name__)


class SQLAlchemyScheduleRepository(ScheduleRepository):
    def __init__(self, session: "AsyncSession"):
        self.session = session

    async def save(
        self, schedules: Iterable["DaySchedule"], dates: date | tuple[date, date]
    ) -> dict[Literal["add", "remove"], set[tuple[date, "Group", "Lesson"]]]:
        schedules_list = list(schedules)
        logger.debug("Saving %d day schedules to database", len(schedules_list))

        _saving_result: dict[
            Literal["add", "remove"], set[tuple[date, Group, Lesson]]
        ] = {"add": set(), "remove": set()}

        for day_schedules in batched(schedules_list, 10):
            _result = await self._save_batch(day_schedules, dates)

            _saving_result["add"].update(_result.get("add", {}))
            _saving_result["remove"].update(_result.get("remove", {}))

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

        return _saving_result

    async def _save_batch(
        self, schedules: Iterable["DaySchedule"], dates: date | tuple[date, date]
    ) -> dict[Literal["add", "remove"], set[tuple[date, "Group", "Lesson"]]]:
        _to_update = await self._check_lessons_updates(schedules, dates)

        _lessons_to_add, _lessons_to_remove = (
            _to_update.get("add", set()),
            _to_update.get("remove", set()),
        )

        if _lessons_to_add or _lessons_to_remove:
            await self._update_schedule(_lessons_to_add, _lessons_to_remove)

        return _to_update

    async def _check_lessons_updates(
        self, schedules: Iterable["DaySchedule"], dates: date | tuple[date, date]
    ) -> dict[Literal["add", "remove"], set[tuple[date, "Group", "Lesson"]]]:
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

        lessons_schedule: set[tuple[date, Group, Lesson]] = {
            (_date, day_schedule.group, lesson)
            for _date in self._expand_dates(dates)
            for day_schedule in schedules
            if day_schedule.lessons
            for lesson in day_schedule.lessons
        }

        return {
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

    @staticmethod
    def _expand_dates(dates: date | tuple[date, date]) -> list[date]:
        if isinstance(dates, date):
            return [dates]
        start, end = dates
        return [
            start + datetime.timedelta(days=i) for i in range((end - start).days + 1)
        ]
