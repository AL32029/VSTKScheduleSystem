from abc import ABC, abstractmethod

from service_bot.domain.entities import Cabinet


class CabinetRepository(ABC):
    @abstractmethod
    async def get_by_number(self, cabinet_number: str) -> 'Cabinet':
        """Получение кабинета по номеру"""
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list['Cabinet']:
        """Получение списка всех кабинетов"""
        raise NotImplementedError
