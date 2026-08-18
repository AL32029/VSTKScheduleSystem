from abc import ABC, abstractmethod
from collections.abc import Iterable

from service_parser.domain.entities import Cabinet


class CabinetRepository(ABC):
    @abstractmethod
    async def save(self, cabinets: Iterable["Cabinet"]) -> None:
        """Сохранение кабинетов в БД"""
        raise NotImplementedError

    @abstractmethod
    async def get_by_index(self, cabinet_index: str) -> "Cabinet | None":
        """Получение кабинета из БД по номеру"""
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list["Cabinet"]:
        """Получение списка всех кабинетов"""
        raise NotImplementedError
