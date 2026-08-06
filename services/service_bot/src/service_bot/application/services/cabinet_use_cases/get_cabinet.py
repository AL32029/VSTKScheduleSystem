from service_bot.application.ports import CabinetRepository
from service_bot.domain.entities import Cabinet


class GetCabinetUseCase:
    """UseCase получения кабинета"""
    def __init__(self, repo: 'CabinetRepository'):
        self.repo = repo

    async def execute(self, cabinet_number: str) -> 'Cabinet':
        cabinet_item = await self.repo.get_by_number(cabinet_number)

        return cabinet_item
