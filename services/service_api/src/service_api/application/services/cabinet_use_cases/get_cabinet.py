import logging

from service_api.application.ports import CabinetRepository, CacheRepository
from service_api.domain.entities import Cabinet
from service_api.domain.exceptions import CacheItemNotFound
from service_api.domain.exceptions.base_exceptions import NotFoundError

logger = logging.getLogger(__name__)


class GetCabinetUseCase:
    def __init__(
        self, cabinet_repo: "CabinetRepository", cache_repo: "CacheRepository"
    ):
        self.cache_repo = cache_repo
        self.cabinet_repo = cabinet_repo

    async def execute(self, cabinet_number: str) -> "Cabinet":
        try:
            logger.info("Obtaining cabinet %s from the cache", cabinet_number)
            cabinet = await self.cache_repo.get_cabinet_cache(cabinet_number)
            logger.info("Cabinet %s has been retrieved from the cache", cabinet.number)
        except CacheItemNotFound:
            logger.warning("Cabinet %s is not found in the cache", cabinet_number)

            logger.info("Obtaining cabinet %s from the database", cabinet_number)
            try:
                cabinet = await self.cabinet_repo.get_by_number(cabinet_number)
            except NotFoundError:
                logger.warning("Cabinet %s is not found in database", cabinet_number)
                raise
            logger.info("Cabinet %s was retrieved from the database", cabinet.number)

            logger.info("Saving cabinet %s to the cache", cabinet.number)
            await self.cache_repo.set_cabinet_cache(cabinet)
            logger.info("Cabinet %s has been saved to the cache", cabinet.number)

        return cabinet
