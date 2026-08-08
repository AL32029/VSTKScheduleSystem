import logging

from service_bot.application.ports import GroupRepository
from service_bot.domain.entities import Group

logger = logging.getLogger(__name__)


class GetAllGroupsUseCase:
    """UseCase получения списка всех кабинетов"""

    def __init__(self, repo: 'GroupRepository'):
        self.repo = repo

    async def execute(self) -> list['Group']:
        logger.info('Loading the list of groups')
        group_items = await self.repo.get_all()
        logger.info('The list of groups has been loaded')

        return group_items
