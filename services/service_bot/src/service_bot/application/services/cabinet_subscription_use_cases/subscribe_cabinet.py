from service_bot.application.ports import UserRepository
from service_bot.domain.entities import Cabinet, User


class SubscribeCabinetUseCase:
    """UseCase подписки на кабинет"""
    def __init__(self, repo: 'UserRepository'):
        self.repo = repo

    async def execute(self, user: 'User', cabinet: 'Cabinet'):
        await self.repo.subscribe_cabinet(user, cabinet)