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

    async def get_by_number(self, group_number: str) -> 'Group':
        """Получение группы по его номеру"""
        request = f'/groups/{group_number}'
        logger.info('Sending an HTTP request GET %s', request)
        resp = await self.client.get(request)

        if resp.status_code == 404 and resp.text == f'Group with number {group_number!r} not found':
            logger.warning('The group %s was not found', group_number)
            raise GroupNotFound(group_number)

        try:
            resp.raise_for_status()
        except HTTPStatusError:
            logger.exception('Error when sending an HTTP request GET %s', request)
            raise

        logger.info('A successful response has been received (status: %s)', resp.status_code)

        return cast('Group', ScheduleItem.model_validate(resp.json()).to_domain('group'))

    async def get_all(self) -> list['Group']:
        """Получение списка всех кабинетов"""
        request = '/groups/'
        logger.info('Sending an HTTP request GET %s', request)
        resp = await self.client.get(request)

        try:
            resp.raise_for_status()
        except HTTPStatusError:
            logger.exception('Error when sending an HTTP request GET %s', request)
            raise

        logger.info('A successful response has been received (status: %s)', resp.status_code)

        return [cast('Group', ScheduleItem.model_validate(group).to_domain('group'))
                for group in resp.json()]
