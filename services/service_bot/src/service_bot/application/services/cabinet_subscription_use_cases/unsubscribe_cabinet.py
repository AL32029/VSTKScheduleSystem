import logging

from service_bot.application.ports import UserRepository
from service_bot.domain.entities import User

logger = logging.getLogger(__name__)


class UnsubscribeCabinetUseCase:
    """UseCase отписки от кабинета"""

    def __init__(self, repo: 'UserRepository'):
        self.repo = repo

    async def execute(self, user: 'User', cabinet_index: str):
        logger.info('Unsubscribing to the %s cabinet', str(cabinet_index))
        await self.repo.unsubscribe_cabinet(user, cabinet_index)
        logger.info('The unsubscription to the %s cabinet has been completed', str(cabinet_index))
