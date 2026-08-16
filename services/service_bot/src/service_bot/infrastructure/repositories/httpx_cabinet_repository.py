import asyncio
import logging
from typing import cast

import httpx
from httpx import AsyncClient, HTTPStatusError

from service_bot.application.ports import CabinetRepository
from service_bot.domain.entities import Cabinet
from service_bot.domain.exceptions import APIRequestTimedOutError, CabinetNotFoundError

from .schemas import ScheduleItem

logger = logging.getLogger(__name__)


class HTTPXCabinetRepository(CabinetRepository):
    """Репозиторий HTTPXCabinetRepository [Реализация репозитория CabinetRepository]"""

    def __init__(self, client: AsyncClient):
        self.client = client

    async def get_by_number(self, cabinet_number: str) -> "Cabinet":
        """Получение кабинета по его номеру"""
        request = f"/cabinets/{cabinet_number}"
        _max_reties = 3

        logger.debug("Requesting cabinet by number %s from API", cabinet_number)

        resp = None

        for attempt in range(_max_reties):
            try:
                resp = await self.client.get(request)

                break
            except (httpx.TimeoutException, TimeoutError) as e:
                if attempt == _max_reties - 1:
                    raise APIRequestTimedOutError(request) from e

                await asyncio.sleep(2**attempt)
                continue

        response_json: dict = resp.json()

        is_success: bool = cast("bool", response_json.get("success"))

        if not is_success and (error := cast("dict", response_json.get("error"))):
            code: str = cast("str", error.get("code"))

            if code is not None and code == "CABINET_NOT_FOUND":
                extra = error.get("extra")
                number = (
                    extra.get("input_number", cabinet_number)
                    if extra is not None
                    else cabinet_number
                )
                logger.warning("Cabinet %s not found in API", number)
                raise CabinetNotFoundError(number)

        try:
            resp.raise_for_status()
        except HTTPStatusError:
            logger.exception("API request failed: GET %s", request)
            raise

        cabinet_json = response_json.get("data")
        cabinet = cast(
            "Cabinet",
            ScheduleItem.model_validate(cabinet_json).to_domain("cabinet"),
        )
        logger.info("Cabinet %s retrieved from API", cabinet.number)
        return cabinet

    async def get_all(self) -> list["Cabinet"]:
        """Получение списка всех кабинетов"""
        request = "/cabinets/"

        _max_reties = 3

        logger.debug("Requesting all cabinets from API")

        resp = None

        for attempt in range(_max_reties):
            try:
                resp = await self.client.get(request)

                break
            except (httpx.TimeoutException, TimeoutError) as e:
                if attempt == _max_reties - 1:
                    raise APIRequestTimedOutError(request) from e

                await asyncio.sleep(2**attempt)
                continue

        response_json: dict = resp.json()

        try:
            resp.raise_for_status()
        except HTTPStatusError:
            logger.exception("API request failed: GET %s", request)
            raise

        cabinets_list = cast("list[dict]", response_json.get("data"))
        cabinets = [
            cast("Cabinet", ScheduleItem.model_validate(cabinet).to_domain("cabinet"))
            for cabinet in cabinets_list
        ]
        logger.info("Retrieved %d cabinets from API", len(cabinets))
        return cabinets
