from abc import ABC, abstractmethod

from service_bot.domain.entities import Group


class GroupRepository(ABC):
    @abstractmethod
    async def get_by_number(self, group_number: str) -> 'Group':
        """Получение группы по номеру"""
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list['Group']:
        """Получение списка всех групп"""
        raise NotImplementedError