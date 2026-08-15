import logging
from typing import Literal

from service_api.application.ports import (
    CabinetRepository,
    CacheRepository,
    ScheduleRepository,
)
from service_api.domain.entities import CabinetDaySchedule
from service_api.domain.exceptions import CacheItemNotFoundError

logger = logging.getLogger(__name__)


class GetCabinetDayScheduleUseCase:
    def __init__(
        self,
        cabinet_repo: "CabinetRepository",
        schedule_repo: "ScheduleRepository",
        cache_repo: "CacheRepository",
    ):
        self.schedule_repo = schedule_repo
        self.cabinet_repo = cabinet_repo
        self.cache_repo = cache_repo

    async def execute(
        self, cabinet_number: str, schedule_to: Literal["today", "tomorrow"]
    ) -> "CabinetDaySchedule":
        try:
            logger.info(
                "Obtaining the lesson schedule for cabinet %s for %s from the cache",
                cabinet_number,
                schedule_to,
            )
            day_schedule = await self.cache_repo.get_cabinet_day_schedule(
                cabinet_number, schedule_to
            )
            logger.info(
                "The lesson schedule for cabinet %s for %s (%s) has been retrieved "
                "from the cache",
                day_schedule.cabinet.number,
                str(day_schedule.date),
                schedule_to,
            )
        except CacheItemNotFoundError:
            logger.warning(
                "The lesson schedule for cabinet %s for %s is not found in the cache",
                cabinet_number,
                schedule_to,
            )

            logger.info("Retrieving cabinet %s from the database", cabinet_number)
            cabinet_item = await self.cabinet_repo.get_by_number(cabinet_number)
            logger.info(
                "Cabinet %s was obtained from the database", cabinet_item.number
            )

            logger.info("Obtaining the date of the lesson schedule for %s", schedule_to)
            schedule_date = await self.schedule_repo.get_schedule_date(schedule_to)
            logger.info(
                "The date of the lesson schedule for %s (%s) has been received",
                schedule_to,
                str(schedule_date),
            )

            logger.info(
                "Obtaining the lesson schedule for cabinet %s for %s (%s) "
                "from the database",
                cabinet_item.number,
                schedule_to,
                str(schedule_date),
            )
            day_schedule = await self.schedule_repo.get_by_cabinet(
                cabinet_item, schedule_to, schedule_date
            )
            logger.info(
                "The lesson schedule for cabinet %s for %s (%s) has been retrieved "
                "from the database",
                cabinet_item.number,
                schedule_to,
                str(schedule_date),
            )

            logger.info(
                "Saving the lesson schedule for cabinet %s for %s (%s) in the cache",
                cabinet_item.number,
                schedule_to,
                str(schedule_date),
            )
            await self.cache_repo.set_cabinet_day_schedule(schedule_to, day_schedule)
            logger.info(
                "The lesson schedule for cabinet %s for %s (%s) has been "
                "saved to the cache",
                cabinet_item.number,
                schedule_to,
                str(schedule_date),
            )

        return day_schedule
