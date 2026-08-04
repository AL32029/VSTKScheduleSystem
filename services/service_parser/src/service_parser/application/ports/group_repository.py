from abc import ABC, abstractmethod
from typing import Iterable

from service_parser.domain.entities import Group


class GroupRepository(ABC):
    @abstractmethod
    async def save(self, group: Iterable['Group']) -> None:
        """Сохранение групп в БД"""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, group: 'Group') -> None:
        """Удаление группы из БД"""
        raise NotImplementedError

    @abstractmethod
    async def get_by_index(self, group_index: str) -> 'Group':
        """Получение группы из БД по индексу"""
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list['Group']:
        """Получение списка всех групп"""
        raise NotImplementedError
