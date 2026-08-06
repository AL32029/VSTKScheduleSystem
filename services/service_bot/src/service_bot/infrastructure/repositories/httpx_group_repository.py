from typing import cast

from httpx import AsyncClient, HTTPStatusError

from service_bot.application.ports import GroupRepository
from service_bot.domain.entities import Group
from service_bot.domain.exceptions import GroupNotFound

from .schemas import ScheduleItem


class HTTPXGroupRepository(GroupRepository):
    """Репозиторий HTTPXGroupRepository [Реализация репозитория GroupRepository]"""

    def __init__(self, client: AsyncClient):
        self.client = client

    async def get_by_number(self, group_number: str) -> 'Group':
        """Получение группы по его номеру"""
        resp = await self.client.get(f'{self.client.base_url}/groups/{group_number}')

        try:
            resp.raise_for_status()
        except HTTPStatusError as e:
            if e.response.is_server_error:
                raise

            if e.response.status_code == 404:
                if 'group' not in str(e).lower():
                    raise

                raise GroupNotFound(group_number)

        return cast('Group', ScheduleItem.model_validate(resp.json()).to_domain('group'))

    async def get_all(self) -> list['Group']:
        """Получение списка всех кабинетов"""
        resp = await self.client.get(f'{self.client.base_url}/groups/')

        return [cast('Group', ScheduleItem.model_validate(group).to_domain('group'))
                for group in resp.json()]
