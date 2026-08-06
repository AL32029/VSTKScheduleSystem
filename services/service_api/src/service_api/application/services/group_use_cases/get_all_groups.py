
from service_api.application.ports import CacheRepository, GroupRepository
from service_api.domain.entities import Group
from service_api.domain.exceptions import CacheItemNotFound


class GetAllGroupsUseCase:
    def __init__(self, group_repo: 'GroupRepository', cache_repo: 'CacheRepository'):
        self.group_repo = group_repo
        self.cache_repo = cache_repo

    async def execute(self) -> list['Group']:
        try:
            groups = await self.cache_repo.get_all_groups_cache()
        except CacheItemNotFound:
            groups = await self.group_repo.get_all()

            await self.cache_repo.set_all_groups_cache(groups)

        return groups
