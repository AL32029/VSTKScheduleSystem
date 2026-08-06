from typing import cast

from httpx import AsyncClient, HTTPStatusError

from service_bot.application.ports import CabinetRepository
from service_bot.domain.entities import Cabinet
from service_bot.domain.exceptions import CabinetNotFound

from .schemas import ScheduleItem


class HTTPXCabinetRepository(CabinetRepository):
    """Репозиторий HTTPXCabinetRepository [Реализация репозитория CabinetRepository]"""
    def __init__(self, client: AsyncClient):
        self.client = client

    async def get_by_number(self, cabinet_number: str) -> 'Cabinet':
        """Получение кабинета по его номеру"""
        resp = await self.client.get(f'{self.client.base_url}/cabinets/{cabinet_number}')

        try:
            resp.raise_for_status()
        except HTTPStatusError as e:
            if e.response.is_server_error:
                raise

            if e.response.status_code == 404:
                raise CabinetNotFound(cabinet_number)

        return cast('Cabinet', ScheduleItem.model_validate(resp.json()).to_domain('cabinet'))

    async def get_all(self) -> list['Cabinet']:
        """Получение списка всех кабинетов"""
        resp = await self.client.get(f'{self.client.base_url}/cabinets/')

        return [cast('Cabinet', ScheduleItem.model_validate(cabinet).to_domain('cabinet'))
                for cabinet in resp.json()]
