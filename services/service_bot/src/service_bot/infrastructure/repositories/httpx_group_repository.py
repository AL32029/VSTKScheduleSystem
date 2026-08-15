import logging
from typing import cast

from httpx import AsyncClient, HTTPStatusError

from service_bot.application.ports import GroupRepository
from service_bot.domain.entities import Group
from service_bot.domain.exceptions import GroupNotFound

from .schemas import ScheduleItem

logger = logging.getLogger(__name__)


class HTTPXGroupRepository(GroupRepository):
    """Репозиторий HTTPXGroupRepository [Реализация репозитория GroupRepository]"""

    def __init__(self, client: AsyncClient):
        self.client = client

    async def get_by_number(self, group_number: str) -> "Group":
        """Получение группы по его номеру"""
        request = f"/groups/{group_number}"
        logger.debug("Requesting group by number %s from API", group_number)
        resp = await self.client.get(request)

        response_json: dict = resp.json()

        is_success: bool = cast(bool, response_json.get("success"))

        if not is_success and (error := cast(dict, response_json.get("error"))):
            code: str = cast(str, error.get("code"))

            if code is not None and code == "GROUP_NOT_FOUND":
                extra = error.get("extra")
                number = (
                    extra.get("input_number", group_number)
                    if extra is not None
                    else group_number
                )
                logger.warning("Group %s not found in API", number)
                raise GroupNotFound(number)

        try:
            resp.raise_for_status()
        except HTTPStatusError:
            logger.exception("API request failed: GET %s", request)
            raise

        group_json = response_json.get("data")
        group = cast(
            "Group", ScheduleItem.model_validate(group_json).to_domain("group")
        )
        logger.info("Group %s retrieved from API", group.number)
        return group

    async def get_all(self) -> list["Group"]:
        """Получение списка всех кабинетов"""
        request = "/groups/"
        logger.debug("Requesting all groups from API")
        resp = await self.client.get(request)

        response_json: dict = resp.json()

        try:
            resp.raise_for_status()
        except HTTPStatusError:
            logger.exception("API request failed: GET %s", request)
            raise

        groups_list = cast(list[dict], response_json.get("data"))
        groups = [
            cast("Group", ScheduleItem.model_validate(group).to_domain("group"))
            for group in groups_list
        ]
        logger.info("Retrieved %d groups from API", len(groups))
        return groups
