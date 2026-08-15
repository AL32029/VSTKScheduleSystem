import logging

from service_bot.application.ports import UserRepository
from service_bot.domain.entities import Cabinet, User

logger = logging.getLogger(__name__)


class SubscribeCabinetUseCase:
    """UseCase подписки на кабинет"""

    def __init__(self, repo: "UserRepository"):
        self.repo = repo

    async def execute(self, user: "User", cabinet: "Cabinet"):
        logger.info("Subscribing to the %s cabinet", str(cabinet))
        await self.repo.subscribe_cabinet(user, cabinet)
        logger.info(
            "The subscription to the %s cabinet has been completed", str(cabinet)
        )
