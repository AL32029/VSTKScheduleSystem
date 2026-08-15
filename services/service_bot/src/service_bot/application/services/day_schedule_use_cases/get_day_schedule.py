import logging
from typing import Literal

from service_bot.application.ports import ScheduleRepository
from service_bot.domain.entities import DaySchedule

logger = logging.getLogger(__name__)


class GetDayScheduleUseCase:
    """UseCase для получения расписанию на конкретную дату"""

    def __init__(self, repo: "ScheduleRepository"):
        self.repo = repo

    async def execute(
        self,
        schedule_item: str,
        schedule_to: Literal["today", "tomorrow"],
        schedule_for: Literal["group", "cabinet"],
    ) -> "DaySchedule":
        logger.info(
            "Obtaining the schedule for %s %s for %s",
            schedule_for,
            schedule_item,
            schedule_to,
        )
        day_schedule = await self.repo.get_day_schedule(
            schedule_item, schedule_to, schedule_for
        )
        logger.info(
            "The schedule for %s %s for %s has been received",
            schedule_for,
            schedule_item,
            schedule_to,
        )

        return day_schedule
