
from service_api.application.ports import CabinetRepository, CacheRepository
from service_api.domain.entities import Cabinet
from service_api.domain.exceptions import CacheItemNotFound


class GetAllCabinetsUseCase:
    def __init__(self, cabinet_repo: 'CabinetRepository', cache_repo: 'CacheRepository'):
        self.cabinet_repo = cabinet_repo
        self.cache_repo = cache_repo

    async def execute(self) -> 'list[Cabinet]':
        try:
            cabinets = await self.cache_repo.get_all_cabinets_cache()
        except CacheItemNotFound:
            cabinets = await self.cabinet_repo.get_all()

            await self.cache_repo.set_all_cabinets_cache(cabinets)

        return cabinets
