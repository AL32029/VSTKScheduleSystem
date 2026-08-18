from abc import ABC, abstractmethod
from collections.abc import Iterable

from service_parser.domain.entities import Group


class GroupRepository(ABC):
    @abstractmethod
    async def save(self, groups: Iterable["Group"]) -> None:
        """Сохранение групп в БД"""
        raise NotImplementedError

    @abstractmethod
    async def deactivate(self, groups: Iterable["Group"]) -> None:
        """Деактивация групп из БД"""
        raise NotImplementedError

    @abstractmethod
    async def get_by_index(self, group_index: str) -> "Group | None":
        """Получение группы из БД по индексу"""
        raise NotImplementedError

    @abstractmethod
    async def get_many(self, groups: Iterable["Group"]) -> list["Group"]:
        """Получение нескольких групп из БД"""
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list["Group"]:
        """Получение списка всех групп"""
        raise NotImplementedError
