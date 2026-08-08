import logging

from service_bot.application.ports import UserRepository
from service_bot.domain.entities import Group, User

logger = logging.getLogger(__name__)


class SubscribeGroupUseCase:
    """UseCase подписки на группу"""

    def __init__(self, repo: 'UserRepository'):
        self.repo = repo

    async def execute(self, user: 'User', group: 'Group'):
        logger.info('Subscribing to the %s group', str(group))
        await self.repo.subscribe_group(user, group)
        logger.info('The subscription to the %s group has been completed', str(group))
