from service_api.application.ports import GroupRepository
from service_api.domain.entities import Group


class GetAllGroupsUseCase:
    def __init__(self, repo: GroupRepository):
        self.repo = repo

    async def execute(self) -> list[Group]:
        return await self.repo.get_all()
