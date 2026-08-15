import datetime
import logging
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
    CabinetDayScheduleNotFoundError,
    GroupDayScheduleNotFoundError,
    ScheduleDateNotFoundError,
)
from service_api.infrastructure.config import system_settings
from service_api.infrastructure.mappers import (
    lessons_orm_to_cabinet_day_schedule_domain,
    lessons_orm_to_group_day_schedule_domain,
)

logger = logging.getLogger(__name__)


class SQLAlchemyScheduleRepository(ScheduleRepository):
    def __init__(self, session: "AsyncSession"):
        self.session = session

    async def get_schedule_date(
        self, schedule_type: Literal["today", "tomorrow"]
    ) -> datetime.date:
        logger.debug("Requesting schedule date for %s from database", schedule_type)
        today = datetime.datetime.now(system_settings.timezone).date()

        stmt = select(
            func.max(LessonORM.date)
            if schedule_type == "today"
            else func.min(LessonORM.date)
        ).where(
            (LessonORM.date <= today)
            if schedule_type == "today"
            else (LessonORM.date > today)
        )

        date: datetime.date | None = await self.session.scalar(stmt)

        if date is None:
            logger.debug("Schedule date for %s not found in database", schedule_type)
            raise ScheduleDateNotFoundError(schedule_type)

        logger.debug("Schedule date for %s found: %s", schedule_type, date.isoformat())
        return date

    async def get_by_group(
        self,
        group: "Group",
        schedule_type: Literal["today", "tomorrow"],
        schedule_date: datetime.date,
        redirect: bool = True,
    ) -> "GroupDaySchedule":
        logger.debug(
            "Requesting schedule for group %s on %s from database",
            group.number,
            schedule_date.isoformat(),
        )
        stmt = (
            select(LessonORM)
            .where(
                LessonORM.group_index == group.index, LessonORM.date == schedule_date
            )
            .order_by(LessonORM.start)
        )

        lessons: Iterable[LessonORM] = (await self.session.scalars(stmt)).all()

        if not lessons:
            logger.debug(
                "Schedule for group %s on %s not found in database",
                group.number,
                schedule_date.isoformat(),
            )
            raise GroupDayScheduleNotFoundError(group, schedule_type, schedule_date)

        logger.debug(
            "Retrieved %d lessons for group %s on %s from database",
            len(lessons),
            group.number,
            schedule_date.isoformat(),
        )
        return lessons_orm_to_group_day_schedule_domain(lessons, redirect)

    async def get_by_cabinet(
        self,
        cabinet: "Cabinet",
        schedule_type: Literal["today", "tomorrow"],
        schedule_date: datetime.date,
        redirect: bool = True,
    ) -> "CabinetDaySchedule":
        logger.debug(
            "Requesting schedule for cabinet %s on %s from database",
            cabinet.number,
            schedule_date.isoformat(),
        )
        stmt = (
            select(LessonORM)
            .join(LessonCabinetORM)
            .where(
                LessonORM.date == schedule_date,
                LessonCabinetORM.cabinet_id == cabinet.index,
            )
            .order_by(LessonORM.start)
        )

        lessons: Iterable[LessonORM] = (await self.session.scalars(stmt)).all()

        if not lessons:
            logger.debug(
                "Schedule for cabinet %s on %s not found in database",
                cabinet.number,
                schedule_date.isoformat(),
            )
            raise CabinetDayScheduleNotFoundError(cabinet, schedule_type, schedule_date)

        logger.debug(
            "Retrieved %d lessons for cabinet %s on %s from database",
            len(lessons),
            cabinet.number,
            schedule_date.isoformat(),
        )
        return lessons_orm_to_cabinet_day_schedule_domain(cabinet, lessons, redirect)
