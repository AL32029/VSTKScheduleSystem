from service_bot.application.ports import CabinetRepository
from service_bot.domain.entities import Cabinet


class GetAllCabinetsUseCase:
    """UseCase получения списка всех кабинетов"""
    def __init__(self, repo: 'CabinetRepository'):
        self.repo = repo

    async def execute(self) -> list['Cabinet']:
        group_items = await self.repo.get_all()

        return group_items