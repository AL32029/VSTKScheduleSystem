import logging

from service_api.application.ports import CacheRepository, GroupRepository
from service_api.domain.entities import Group
from service_api.domain.exceptions import CacheItemNotFound
from service_api.domain.exceptions.base_exceptions import NotFoundError

logger = logging.getLogger(__name__)


class GetGroupUseCase:
    def __init__(self, group_repo: "GroupRepository", cache_repo: "CacheRepository"):
        self.cache_repo = cache_repo
        self.group_repo = group_repo

    async def execute(self, group_number: str) -> "Group":
        try:
            logger.info("Obtaining group %s from the cache", group_number)
            group = await self.cache_repo.get_group_cache(group_number)
            logger.info("Group %s has been retrieved from the cache", group.number)
        except CacheItemNotFound:
            logger.warning("Group %s is not found in the cache", group_number)

            logger.info("Obtaining group %s from the database", group_number)
            try:
                group = await self.group_repo.get_by_number(group_number)
            except NotFoundError:
                logger.warning("Group %s is not found in database", group_number)
                raise
            logger.info("Group %s was retrieved from the database", group.number)

            logger.info("Saving group %s to the cache", group.number)
            await self.cache_repo.set_group_cache(group)
            logger.info("Group %s has been saved to the cache", group.number)

        return group
