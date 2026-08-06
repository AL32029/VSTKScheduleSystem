from service_bot.application.ports import UserRepository
from service_bot.domain.entities import Group, User


class SubscribeGroupUseCase:
    """UseCase подписки на группу"""
    def __init__(self, repo: 'UserRepository'):
        self.repo = repo

    async def execute(self, user: 'User', group: 'Group'):
        await self.repo.subscribe_group(user, group)