import datetime
from collections.abc import Iterable
from typing import Literal

from schedule_db_models import LessonCabinetORM, LessonORM
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from service_api.application.ports import ScheduleRepository
from service_api.domain.entities import (
    Cabinet,
    CabinetDaySchedule,
    Group,
    GroupDaySchedule,
)
from service_api.domain.exceptions import (
    CabinetDayScheduleNotFound,
    GroupDayScheduleNotFound,
    ScheduleDateNotFound,
)
from service_api.infrastructure.config import system_settings
from service_api.infrastructure.mappers import (
    lessons_orm_to_cabinet_day_schedule_domain,
    lessons_orm_to_group_day_schedule_domain,
)


class SQLAlchemyScheduleRepository(ScheduleRepository):
    def __init__(self, session: 'AsyncSession'):
        self.session = session

    async def get_schedule_date(self, schedule_type: Literal['today', 'tomorrow']) -> datetime.date:
        today = datetime.datetime.now(system_settings.TIMEZONE).date()

        stmt = (
            select(func.max(LessonORM.date) if schedule_type == 'today' else func.min(LessonORM.date)).
            where(
                (LessonORM.date <= today) if schedule_type == 'today' else (LessonORM.date > today)
            )
        )

        date: datetime.date | None = await self.session.scalar(stmt)

        if date is None:
            raise ScheduleDateNotFound(schedule_type)

        return date

    async def get_by_group(self, group: 'Group', schedule_type: Literal['today', 'tomorrow'],
                           schedule_date: datetime.date, redirect: bool = True) -> 'GroupDaySchedule':
        stmt = (
            select(LessonORM).
            where(LessonORM.group_index == group.index, LessonORM.date == schedule_date).
            order_by(LessonORM.start)
        )

        lessons: Iterable[LessonORM] = (await self.session.scalars(stmt)).all()

        if not lessons:
            raise GroupDayScheduleNotFound(group, schedule_type, schedule_date)

        return lessons_orm_to_group_day_schedule_domain(lessons, redirect)

    async def get_by_cabinet(self, cabinet: 'Cabinet', schedule_type: Literal['today', 'tomorrow'],
                             schedule_date: datetime.date, redirect: bool = True) -> 'CabinetDaySchedule':
        stmt = (
            select(LessonORM).
            join(LessonCabinetORM).
            where(
                LessonORM.date == schedule_date,
                LessonCabinetORM.cabinet_id == cabinet.index
            ).
            order_by(LessonORM.start)
        )

        lessons: Iterable[LessonORM] = (await self.session.scalars(stmt)).all()

        if not lessons:
            raise CabinetDayScheduleNotFound(cabinet, schedule_type, schedule_date)

        return lessons_orm_to_cabinet_day_schedule_domain(cabinet, lessons, redirect)
