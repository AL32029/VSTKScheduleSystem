import datetime
from collections import defaultdict
from collections.abc import Iterable
from itertools import batched

from schedule_db_models import GroupORM, LessonORM
from sqlalchemy import and_, delete, exists, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from service_parser.application.ports import ScheduleRepository
from service_parser.domain.entities import DaySchedule, Group
from service_parser.domain.exceptions import DayScheduleNotFound, GroupNotFound
from service_parser.infrastructure.domain_mappers import (
    group_orm_to_domain,
    lesson_domain_in_orm,
    lessons_orm_to_day_schedule_domain,
)


class SQLAlchemyScheduleRepository(ScheduleRepository):
    def __init__(self, session: 'AsyncSession'):
        self.session = session

    async def save(self, day_schedules: Iterable['DaySchedule']) -> None:
        schedule_groups = {day_schedule.group for day_schedule in day_schedules}
        database_groups = {
            group_orm_to_domain(group)
            async for group in await self.session.stream_scalars(
                select(GroupORM).where(GroupORM.index.in_({group.index for group in schedule_groups}))
            )
        }

        if schedule_groups - database_groups:
            raise GroupNotFound(f'The following groups are missing: '
                                f'{', '.join(str(group) for group in schedule_groups - database_groups)}')

        schedule_updates = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        for schedules in batched(day_schedules, 250):
            db_schedules = await self.get_many_by_groups([
                (day_schedule.group, day_schedule.date)
                for day_schedule in schedules
            ])

            schedules_check: set[tuple[DaySchedule, DaySchedule | None]] = {
                (
                    day_schedule,
                    next(
                        (db_schedule
                         for db_schedule in db_schedules
                         if db_schedule.date == day_schedule.date and db_schedule.group == day_schedule.group),
                        None
                    )
                )
                for day_schedule in schedules
            }

            for day_schedule, db_schedule in schedules_check:
                if db_schedule is None:
                    schedule_updates['add'][day_schedule.date][day_schedule.group].extend(day_schedule.lessons)
                    continue

                if day_schedule == db_schedule:
                    continue

                day_schedule_lessons = {*day_schedule.lessons}
                db_schedule_lessons = {*db_schedule.lessons}

                schedule_updates['add'][day_schedule.date][day_schedule.group].extend(
                    day_schedule_lessons - db_schedule_lessons
                )
                schedule_updates['remove'][day_schedule.date][day_schedule.group].extend(
                    db_schedule_lessons - day_schedule_lessons
                )

        if 'remove' in schedule_updates:
            for schedule_updates_items in batched(schedule_updates['remove'].items(), 5):
                stmt = (
                    delete(LessonORM).
                    where(or_(*[
                        and_(
                            LessonORM.date == date,
                            LessonORM.group_index == group.index,
                            LessonORM.start == lesson.start,
                            LessonORM.end == lesson.end,
                            LessonORM.name == lesson.name
                        )
                        for date, groups in schedule_updates_items if groups
                        for group, lessons in groups.items() if lessons
                        for lesson in lessons
                    ]))
                )

                await self.session.execute(stmt)

        if 'add' in schedule_updates:
            for schedule_updates_items in batched(schedule_updates['add'].items(), 10):
                lessons_add = []

                lessons_add.extend(
                    lesson_domain_in_orm(date, group, lesson)
                    for date, groups in schedule_updates_items if groups
                    for group, lessons in groups.items() if lessons
                    for lesson in lessons
                )

                self.session.add_all(lessons_add)

        await self.session.commit()

    async def get_by_group(self, group: 'Group', date: datetime.date) -> 'DaySchedule':
        group_is_exists = await self.session.scalar(
            select(exists(GroupORM).where(GroupORM.index == group.index))
        )

        if not group_is_exists:
            raise GroupNotFound(f'Group {str(group)!r} not found')

        stmt = (
            select(LessonORM).
            where(
                LessonORM.group_index == group.index,
                LessonORM.date == date
            )
        )

        lessons = (await self.session.scalars(stmt)).all()

        if not lessons:
            raise DayScheduleNotFound(f'Day schedule at {date!s} for group {str(group)!r} not found')

        return lessons_orm_to_day_schedule_domain(lessons)

    async def get_many_by_groups(self, items: Iterable[tuple['Group', datetime.date]]) -> set['DaySchedule']:
        schedule_groups = {group for group, _ in items}

        db_groups = {
            group_orm_to_domain(group)
            async for group in await self.session.stream_scalars(
                select(GroupORM).
                where(GroupORM.index.in_(schedule_group.index for schedule_group in schedule_groups))
            )
        }

        if schedule_groups - db_groups:
            raise GroupNotFound(f'The following groups are missing: '
                                f'{', '.join(str(group) for group in schedule_groups - db_groups)}')

        items_return = defaultdict(lambda: defaultdict(list))

        for batched_items in batched(set(items), 250):
            stmt = (
                select(LessonORM).
                where(or_(*[
                    and_(
                        LessonORM.group_index == group.index,
                        LessonORM.date == date
                    )
                    for group, date in batched_items
                ]))
            )

            async for lesson in await self.session.stream_scalars(stmt):
                items_return[lesson.date][group_orm_to_domain(lesson.group)].append(lesson)

        return {
            lessons_orm_to_day_schedule_domain(lessons)
            for date, groups in items_return.items() if groups
            for group, lessons in groups.items() if lessons
        }
