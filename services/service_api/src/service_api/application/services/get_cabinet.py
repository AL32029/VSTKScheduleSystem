from service_api.application.ports import CabinetRepository
from service_api.domain.entities import Cabinet


class GetCabinetUseCase:
    def __init__(self, repo: CabinetRepository):
        self.repo = repo

    async def execute(self, cabinet_number) -> Cabinet:
        return await self.repo.get_by_number(cabinet_number)