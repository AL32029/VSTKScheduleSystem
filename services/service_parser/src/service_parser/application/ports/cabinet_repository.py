from abc import ABC, abstractmethod
from typing import Iterable

from service_parser.domain.entities import Cabinet


class CabinetRepository(ABC):
    @abstractmethod
    async def save(self, cabinet: Cabinet) -> None:
        """Сохранение кабинета в БД"""
        raise NotImplementedError

    @abstractmethod
    async def save_all(self, cabinets: Iterable[Cabinet]) -> None:
        """Массовое сохранение кабинетов в БД"""
        raise NotImplementedError

    @abstractmethod
    async def get_by_index(self, cabinet_index: str) -> Cabinet:
        """Получение кабинета из БД по номеру"""
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> Iterable[Cabinet]:
        """Получение списка всех кабинетов"""
        raise NotImplementedError
