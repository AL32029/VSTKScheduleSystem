from abc import ABC, abstractmethod

from service_api.domain.entities import Group


class GroupRepository(ABC):
    @abstractmethod
    async def get_by_number(self, number: str) -> 'Group':
        """Получение группы по номеру"""
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> 'list[Group]':
        """Получение всех групп"""
        raise NotImplementedError
