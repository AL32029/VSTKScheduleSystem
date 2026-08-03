
from service_api.application.ports import CacheRepository, GroupRepository
from service_api.domain.entities import Group
from service_api.domain.exceptions import CacheItemNotFound


class GetGroupUseCase:
    def __init__(self, group_repo: GroupRepository, cache_repo: CacheRepository):
        self.cache_repo = cache_repo
        self.group_repo = group_repo

    async def execute(self, group_number: str) -> Group:
        try:
            group = await self.cache_repo.get_group_cache(group_number)
        except CacheItemNotFound:
            group = await self.group_repo.get_by_number(group_number)

            await self.cache_repo.set_group_cache(group)

        return group
