from typing import Iterable

from service_parser.application.ports import CabinetRepository
from service_parser.domain.entities import Cabinet


def _get_cabinet_model(cabinet: str | Cabinet) -> Cabinet:
    return cabinet if isinstance(cabinet, Cabinet) else Cabinet(cabinet)


class CabinetUseCase:
    def __init__(self, cabinet_repo: CabinetRepository):
        self.repo = cabinet_repo


class CreateCabinetUseCase(CabinetUseCase):
    async def execute(self, cabinet: str | Cabinet) -> Cabinet:
        cabinet_model = _get_cabinet_model(cabinet)

        await self.repo.save([cabinet_model])

        return cabinet_model


class GetCabinetByIndexUseCase(CabinetUseCase):
    async def execute(self, cabinet: str | Cabinet) -> Cabinet:
        cabinet_db = await self.repo.get_by_index(_get_cabinet_model(cabinet).index)

        return cabinet_db


class GetAllCabinetsUseCase(CabinetUseCase):
    async def execute(self) -> Iterable[Cabinet]:
        cabinets = await self.repo.get_all()

        return cabinets
