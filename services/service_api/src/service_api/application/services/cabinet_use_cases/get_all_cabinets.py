import logging

from service_api.application.ports import CabinetRepository, CacheRepository
from service_api.domain.entities import Cabinet
from service_api.domain.exceptions import CacheItemNotFoundError

logger = logging.getLogger(__name__)


class GetAllCabinetsUseCase:
    def __init__(
        self, cabinet_repo: "CabinetRepository", cache_repo: "CacheRepository"
    ):
        self.cabinet_repo = cabinet_repo
        self.cache_repo = cache_repo

    async def execute(self) -> list["Cabinet"]:
        try:
            logger.info("Obtaining list of cabinets from the cache")
            cabinets = await self.cache_repo.get_all_cabinets_cache()
            logger.info("Obtaining list of cabinets has been retrieved from the cache")
        except CacheItemNotFoundError:
            logger.warning("List of cabinets is not found in the cache")

            logger.info("Obtaining list of cabinets from the database")
            cabinets = await self.cabinet_repo.get_all()
            logger.info("List of cabinets was retrieved from the database")

            logger.info("Saving list of cabinets to the cache")
            await self.cache_repo.set_all_cabinets_cache(cabinets)
            logger.info("List of cabinets has been saved to the cache")

        return cabinets
