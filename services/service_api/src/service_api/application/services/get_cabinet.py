
from service_api.application.ports import CabinetRepository, CacheRepository
from service_api.domain.entities import Cabinet
from service_api.domain.exceptions import CacheItemNotFound


class GetCabinetUseCase:
    def __init__(self, cabinet_repo: CabinetRepository, cache_repo: CacheRepository):
        self.cache_repo = cache_repo
        self.cabinet_repo = cabinet_repo

    async def execute(self, cabinet_number: str) -> Cabinet:
        try:
            cabinet = await self.cache_repo.get_cabinet_cache(cabinet_number)
        except CacheItemNotFound:
            cabinet = await self.cabinet_repo.get_by_number(cabinet_number)

            await self.cache_repo.set_cabinet_cache(cabinet)

        return cabinet
