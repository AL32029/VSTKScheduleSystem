from service_bot.application.ports import GroupRepository
from service_bot.domain.entities import Group


class GetGroupUseCase:
    """UseCase получения группы"""
    def __init__(self, repo: 'GroupRepository'):
        self.repo = repo

    async def execute(self, group_number: str) -> 'Group':
        group_item = await self.repo.get_by_number(group_number)

        return group_item
