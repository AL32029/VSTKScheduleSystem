import datetime
import logging
from typing import Literal, cast

from httpx import AsyncClient, HTTPStatusError

from service_bot.application.ports import ScheduleRepository
from service_bot.domain.entities import Cabinet, DaySchedule, Group
from service_bot.domain.exceptions import (
    CabinetNotFoundError,
    GroupNotFoundError,
    ScheduleDateNotFoundError,
    ScheduleForCabinetNotFoundError,
    ScheduleForGroupNotFoundError,
)
from service_bot.infrastructure.repositories.schemas import DayScheduleItem

logger = logging.getLogger(__name__)


class HTTPXScheduleRepository(ScheduleRepository):
    """Репозиторий HTTPXScheduleRepository
    [Реализация репозитория ScheduleRepository]"""

    def __init__(self, client: "AsyncClient"):
        self.client = client

    async def get_day_schedule(
        self,
        schedule_item: str,
        schedule_to: Literal["today", "tomorrow"],
        schedule_for: Literal["group", "cabinet"],
    ) -> "DaySchedule":
        """Получение расписания на конкретную дату"""
        request = f"/schedule/{schedule_for}"
        logger.debug(
            "Requesting %s schedule for %s (%s) from API",
            schedule_for,
            schedule_item,
            schedule_to,
        )
        resp = await self.client.get(
            request,
            params={
                f"{schedule_for}_number": schedule_item,
                "schedule_to": schedule_to,
            },
        )

        response_json: dict = resp.json()

        is_success: bool = cast("bool", response_json.get("success"))

        if (
            not is_success
            and (error := cast("dict", response_json.get("error")))
            and (code := cast("str", error.get("code")))
        ):
            extra = error.get("extra")
            if code in ["GROUP_NOT_FOUND", "CABINET_NOT_FOUND"]:
                number = (
                    extra.get("input_number", schedule_item)
                    if extra is not None
                    else schedule_item
                )
                logger.warning(
                    "%s %s not found in API",
                    "Group" if code == "GROUP_NOT_FOUND" else "Cabinet",
                    number,
                )
                raise (
                    GroupNotFoundError
                    if code == "GROUP_NOT_FOUND"
                    else CabinetNotFoundError
                )(number)

            if code == "SCHEDULE_DATE_NOT_FOUND":
                schedule_at = (
                    extra.get("schedule_to", schedule_to)
                    if extra is not None
                    else schedule_to
                )
                logger.warning("Schedule date for %s not published yet", schedule_at)
                raise ScheduleDateNotFoundError(schedule_to)

            if code in [
                "SCHEDULE_FOR_GROUP_NOT_FOUND",
                "SCHEDULE_FOR_CABINET_NOT_FOUND",
            ]:
                schedule_item_type = (
                    "group" if code == "SCHEDULE_FOR_GROUP_NOT_FOUND" else "cabinet"
                )
                item = (Group if schedule_item_type == "group" else Cabinet)(
                    **extra["item"],
                )
                schedule_at = (
                    extra.get("schedule_to", schedule_to)
                    if extra is not None
                    else schedule_to
                )
                schedule_date = datetime.date.fromisoformat(extra["schedule_date"])
                logger.warning(
                    "No lessons found for %s %s on %s (%s)",
                    schedule_item_type.capitalize(),
                    item.number,
                    schedule_at,
                    schedule_date,
                )
                raise (
                    ScheduleForGroupNotFoundError
                    if schedule_item_type == "group"
                    else ScheduleForCabinetNotFoundError
                )(item, schedule_at, schedule_date)

        try:
            resp.raise_for_status()
        except HTTPStatusError:
            logger.exception("API request failed: GET %s", request)
            raise

        day_schedule_json = response_json.get("data")
        day_schedule = DayScheduleItem.model_validate(day_schedule_json).to_domain(
            schedule_for,
        )
        logger.info(
            "Retrieved schedule for %s %s (%s) from API",
            schedule_for,
            schedule_item,
            schedule_to,
        )
        return day_schedule
