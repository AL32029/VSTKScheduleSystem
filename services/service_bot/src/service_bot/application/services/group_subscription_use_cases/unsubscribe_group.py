import logging

from service_bot.application.ports import UserRepository
from service_bot.domain.entities import User

logger = logging.getLogger(__name__)


class UnsubscribeGroupUseCase:
    """UseCase отписки от группы"""

    def __init__(self, repo: "UserRepository"):
        self.repo = repo

    async def execute(self, user: "User", group_index: str):
        logger.info("Unsubscribing to the %s group", str(group_index))
        await self.repo.unsubscribe_group(user, group_index)
        logger.info(
            "The unsubscription to the %s group has been completed", str(group_index),
        )
