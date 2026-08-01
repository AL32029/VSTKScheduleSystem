from service_api.application.ports import CabinetRepository
from service_api.domain.entities import Cabinet


class GetAllCabinetsUseCase:
    def __init__(self, repo: CabinetRepository):
        self.repo = repo

    async def execute(self) -> list[Cabinet]:
        return await self.repo.get_all()
