import logging

from service_api.application.ports import CacheRepository, GroupRepository
from service_api.domain.entities import Group
from service_api.domain.exceptions import CacheItemNotFound

logger = logging.getLogger(__name__)


class GetAllGroupsUseCase:
    def __init__(self, group_repo: "GroupRepository", cache_repo: "CacheRepository"):
        self.group_repo = group_repo
        self.cache_repo = cache_repo

    async def execute(self) -> list["Group"]:
        try:
            logger.info("Obtaining list of groups from the cache")
            groups = await self.cache_repo.get_all_groups_cache()
            logger.info("List of groups has been retrieved from the cache")
        except CacheItemNotFound:
            logger.warning("List of groups is not found in the cache")

            logger.info("Obtaining list of groups from the database")
            groups = await self.group_repo.get_all()
            logger.info("List of groups was retrieved from the database")

            logger.info("Saving list of groups to the cache")
            await self.cache_repo.set_all_groups_cache(groups)
            logger.info("List of groups has been saved to the cache")

        return groups
