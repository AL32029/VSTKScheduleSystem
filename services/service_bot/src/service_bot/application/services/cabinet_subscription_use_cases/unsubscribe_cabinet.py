from service_bot.application.ports import UserRepository
from service_bot.domain.entities import User


class UnsubscribeCabinetUseCase:
    """UseCase отписки от кабинета"""
    def __init__(self, repo: 'UserRepository'):
        self.repo = repo

    async def execute(self, user: 'User', cabinet_index: str):
        await self.repo.unsubscribe_cabinet(user, cabinet_index)