import logging
from typing import Literal

from service_api.application.ports import (
    CacheRepository,
    GroupRepository,
    ScheduleRepository,
)
from service_api.domain.entities import GroupDaySchedule
from service_api.domain.exceptions import CacheItemNotFoundError

logger = logging.getLogger(__name__)


class GetGroupDayScheduleUseCase:
    def __init__(
        self,
        group_repo: "GroupRepository",
        schedule_repo: "ScheduleRepository",
        cache_repo: "CacheRepository",
    ):
        self.schedule_repo = schedule_repo
        self.group_repo = group_repo
        self.cache_repo = cache_repo

    async def execute(
        self, group_number: str, schedule_to: Literal["today", "tomorrow"]
    ) -> "GroupDaySchedule":
        try:
            logger.info(
                "Obtaining the lesson schedule for group %s for %s from the cache",
                group_number,
                schedule_to,
            )
            day_schedule = await self.cache_repo.get_group_day_schedule(
                schedule_to, group_number
            )
            logger.info(
                "The lesson schedule for group %s for %s (%s) "
                "has been retrieved from the cache",
                day_schedule.group.number,
                str(day_schedule.date),
                schedule_to,
            )
        except CacheItemNotFoundError:
            logger.warning(
                "The lesson schedule for group %s for %s is not found in the cache",
                group_number,
                schedule_to,
            )

            logger.info("Retrieving group %s from the database", group_number)
            group_item = await self.group_repo.get_by_number(group_number)
            logger.info("Group %s was obtained from the database", group_item.number)

            logger.info("Obtaining the date of the lesson schedule for %s", schedule_to)
            schedule_date = await self.schedule_repo.get_schedule_date(schedule_to)
            logger.info(
                "The date of the lesson schedule for %s (%s) has been received",
                schedule_to,
                str(schedule_date),
            )

            logger.info(
                "Obtaining the lesson schedule for group %s for %s (%s) "
                "from the database",
                group_item.number,
                schedule_to,
                str(schedule_date),
            )
            day_schedule = await self.schedule_repo.get_by_group(
                group_item, schedule_to, schedule_date
            )

            logger.info(
                "Saving the lesson schedule for group %s for %s (%s) in the cache",
                group_item.number,
                schedule_to,
                str(schedule_date),
            )
            await self.cache_repo.set_group_day_schedule(schedule_to, day_schedule)
            logger.info(
                "The lesson schedule for group %s for %s (%s) "
                "has been saved to the cache",
                group_item.number,
                schedule_to,
                str(schedule_date),
            )

        return day_schedule
