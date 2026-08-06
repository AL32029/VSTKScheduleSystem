from service_bot.application.ports import GroupRepository
from service_bot.domain.entities import Group


class GetAllGroupsUseCase:
    """UseCase получения списка всех кабинетов"""
    def __init__(self, repo: 'GroupRepository'):
        self.repo = repo

    async def execute(self) -> list['Group']:
        group_items = await self.repo.get_all()

        return group_items