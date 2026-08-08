import logging
from typing import cast

from httpx import AsyncClient, HTTPStatusError

from service_bot.application.ports import CabinetRepository
from service_bot.domain.entities import Cabinet
from service_bot.domain.exceptions import CabinetNotFound

from .schemas import ScheduleItem

logger = logging.getLogger(__name__)


class HTTPXCabinetRepository(CabinetRepository):
    """Репозиторий HTTPXCabinetRepository [Реализация репозитория CabinetRepository]"""

    def __init__(self, client: AsyncClient):
        self.client = client

    async def get_by_number(self, cabinet_number: str) -> 'Cabinet':
        """Получение кабинета по его номеру"""
        request = f'/cabinets/{cabinet_number}'
        logger.info('Sending an HTTP request GET %s', request)
        resp = await self.client.get(request)

        if resp.status_code == 404 and resp.text == f'Cabinet with number {cabinet_number!r} not found':
            logger.warning('The cabinet %s was not found', cabinet_number)
            raise CabinetNotFound(cabinet_number)

        try:
            resp.raise_for_status()
        except HTTPStatusError:
            logger.exception('Error when sending an HTTP request GET %s', request)
            raise

        logger.info('A successful response has been received (status: %s)', resp.status_code)

        return cast('Cabinet', ScheduleItem.model_validate(resp.json()).to_domain('cabinet'))

    async def get_all(self) -> list['Cabinet']:
        """Получение списка всех кабинетов"""
        request = '/cabinets/'
        logger.info('Sending an HTTP request GET %s', request)
        resp = await self.client.get(request)

        try:
            resp.raise_for_status()
        except HTTPStatusError:
            logger.exception('Error when sending an HTTP request GET %s', request)
            raise

        logger.info('A successful response has been received (status: %s)', resp.status_code)

        return [cast('Cabinet', ScheduleItem.model_validate(cabinet).to_domain('cabinet'))
                for cabinet in resp.json()]
