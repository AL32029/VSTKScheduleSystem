from service_api.application.ports import GroupRepository
from service_api.domain.entities import Group


class GetGroupUseCase:
    def __init__(self, repo: GroupRepository):
        self.repo = repo

    async def execute(self, group_number) -> Group:
        return await self.repo.get_by_number(group_number)