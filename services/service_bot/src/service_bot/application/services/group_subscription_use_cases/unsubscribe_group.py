from service_bot.application.ports import UserRepository
from service_bot.domain.entities import User


class UnsubscribeGroupUseCase:
    """UseCase отписки от группы"""
    def __init__(self, repo: 'UserRepository'):
        self.repo = repo

    async def execute(self, user: 'User', group_index: str):
        await self.repo.unsubscribe_group(user, group_index)