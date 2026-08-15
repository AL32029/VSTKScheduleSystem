import datetime
import logging
from collections import defaultdict
from collections.abc import Iterable
from itertools import batched

from schedule_db_models import GroupORM, LessonORM
from sqlalchemy import and_, delete, exists, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from service_parser.application.ports import ScheduleRepository
from service_parser.domain.entities import DaySchedule, Group
from service_parser.domain.exceptions import (
    DayScheduleNotFoundError,
    GroupNotFoundError,
)
from service_parser.infrastructure.domain_mappers import (
    group_orm_to_domain,
    lesson_domain_in_orm,
    lessons_orm_to_day_schedule_domain,
)

logger = logging.getLogger(__name__)


class SQLAlchemyScheduleRepository(ScheduleRepository):
    def __init__(self, session: "AsyncSession"):
        self.session = session

    async def save(self, day_schedules: Iterable["DaySchedule"]) -> None:  # noqa: C901
        schedules_list = list(day_schedules)
        logger.debug("Saving %d day schedules to database", len(schedules_list))

        schedule_groups = {day_schedule.group for day_schedule in schedules_list}
        logger.debug(
            "Checking existence of %d groups in database", len(schedule_groups)
        )
        database_groups = {
            group_orm_to_domain(group)
            async for group in await self.session.stream_scalars(
                select(GroupORM).where(
                    GroupORM.index.in_({group.index for group in schedule_groups})
                )
            )
        }

        if schedule_groups - database_groups:
            missing = ", ".join(
                str(group) for group in schedule_groups - database_groups
            )
            logger.debug("Missing groups: %s", missing)
            raise GroupNotFoundError(f"The following groups are missing: {missing}")

        logger.debug("All groups exist, computing differences")
        schedule_updates = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        total_added = 0
        total_removed = 0

        for schedules in batched(schedules_list, 250):
            db_schedules = await self.get_many_by_groups(
                [(day_schedule.group, day_schedule.date) for day_schedule in schedules]
            )

            schedules_check: set[tuple[DaySchedule, DaySchedule | None]] = {
                (
                    day_schedule,
                    next(
                        (
                            db_schedule
                            for db_schedule in db_schedules
                            if db_schedule.date == day_schedule.date
                            and db_schedule.group == day_schedule.group
                        ),
                        None,
                    ),
                )
                for day_schedule in schedules
            }

            for day_schedule, db_schedule in schedules_check:
                if db_schedule is None:
                    schedule_updates["add"][day_schedule.date][
                        day_schedule.group
                    ].extend(day_schedule.lessons)
                    continue

                if day_schedule == db_schedule:
                    continue

                day_schedule_lessons = {*day_schedule.lessons}
                db_schedule_lessons = {*db_schedule.lessons}

                added = day_schedule_lessons - db_schedule_lessons
                removed = db_schedule_lessons - day_schedule_lessons

                if added:
                    schedule_updates["add"][day_schedule.date][
                        day_schedule.group
                    ].extend(added)
                    total_added += len(added)
                if removed:
                    schedule_updates["remove"][day_schedule.date][
                        day_schedule.group
                    ].extend(removed)
                    total_removed += len(removed)

        if "remove" in schedule_updates:
            logger.debug("Removing %d lessons from database", total_removed)
            for schedule_updates_items in batched(
                schedule_updates["remove"].items(), 5
            ):
                stmt = delete(LessonORM).where(
                    or_(
                        *[
                            and_(
                                LessonORM.date == date,
                                LessonORM.group_index == group.index,
                                LessonORM.start == lesson.start,
                                LessonORM.end == lesson.end,
                                LessonORM.name == lesson.name,
                            )
                            for date, groups in schedule_updates_items
                            if groups
                            for group, lessons in groups.items()
                            if lessons
                            for lesson in lessons
                        ]
                    )
                )

                await self.session.execute(stmt)

        if "add" in schedule_updates:
            logger.debug("Adding %d lessons to database", total_added)
            for schedule_updates_items in batched(schedule_updates["add"].items(), 10):
                lessons_add = []

                lessons_add.extend(
                    lesson_domain_in_orm(date, group, lesson)
                    for date, groups in schedule_updates_items
                    if groups
                    for group, lessons in groups.items()
                    if lessons
                    for lesson in lessons
                )

                self.session.add_all(lessons_add)

        await self.session.commit()
        logger.debug(
            "Schedule save completed: %d schedules processed, %d lessons added, "
            "%d lessons removed",
            len(schedules_list),
            total_added,
            total_removed,
        )

    async def get_by_group(self, group: "Group", date: datetime.date) -> "DaySchedule":
        logger.debug(
            "Requesting schedule for group %s on %s from database",
            group.number,
            date.isoformat(),
        )

        group_is_exists = await self.session.scalar(
            select(exists(GroupORM).where(GroupORM.index == group.index))
        )

        if not group_is_exists:
            logger.debug("Group %s not found in database", group.number)
            raise GroupNotFoundError(f"Group {str(group)!r} not found")

        stmt = select(LessonORM).where(
            LessonORM.group_index == group.index, LessonORM.date == date
        )

        lessons = (await self.session.scalars(stmt)).all()

        if not lessons:
            logger.debug(
                "Schedule for group %s on %s not found", group.number, date.isoformat()
            )
            raise DayScheduleNotFoundError(
                f"Day schedule at {date!s} for group {str(group)!r} not found"
            )

        logger.debug(
            "Retrieved %d lessons for group %s on %s",
            len(lessons),
            group.number,
            date.isoformat(),
        )
        return lessons_orm_to_day_schedule_domain(lessons)

    async def get_many_by_groups(
        self, items: Iterable[tuple["Group", datetime.date]]
    ) -> set["DaySchedule"]:
        items_list = list(items)
        logger.debug(
            "Requesting schedules for %d group-date pairs from database",
            len(items_list),
        )

        schedule_groups = {group for group, _ in items_list}

        db_groups = {
            group_orm_to_domain(group)
            async for group in await self.session.stream_scalars(
                select(GroupORM).where(
                    GroupORM.index.in_(
                        schedule_group.index for schedule_group in schedule_groups
                    )
                )
            )
        }

        if schedule_groups - db_groups:
            missing = ", ".join(str(group) for group in schedule_groups - db_groups)
            logger.debug("Missing groups: %s", missing)
            raise GroupNotFoundError(f"The following groups are missing: {missing}")

        items_return = defaultdict(lambda: defaultdict(list))
        total_lessons = 0

        for batched_items in batched(set(items_list), 250):
            stmt = select(LessonORM).where(
                or_(
                    *[
                        and_(
                            LessonORM.group_index == group.index, LessonORM.date == date
                        )
                        for group, date in batched_items
                    ]
                )
            )

            async for lesson in await self.session.stream_scalars(stmt):
                items_return[lesson.date][group_orm_to_domain(lesson.group)].append(
                    lesson
                )
                total_lessons += 1

        result = {
            lessons_orm_to_day_schedule_domain(lessons)
            for date, groups in items_return.items()
            if groups
            for group, lessons in groups.items()
            if lessons
        }

        logger.debug(
            "Retrieved %d day schedules with %d total lessons from database",
            len(result),
            total_lessons,
        )
        return result
