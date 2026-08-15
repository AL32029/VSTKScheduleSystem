from abc import ABC, abstractmethod

from service_api.domain.entities import Cabinet


class CabinetRepository(ABC):
    @abstractmethod
    async def get_by_number(self, number: str) -> "Cabinet":
        """Получение кабинета по номеру"""
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list["Cabinet"]:
        """Получение всех кабинетов"""
        raise NotImplementedError
