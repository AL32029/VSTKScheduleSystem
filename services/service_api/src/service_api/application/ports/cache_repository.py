from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Literal

from service_api.domain.entities import (
    Cabinet,
    CabinetDaySchedule,
    Group,
    GroupDaySchedule,
)


class CacheRepository(ABC):
    @abstractmethod
    async def get_group_cache(self, group_number: str) -> "Group":
        """Получение группы из кэша"""
        raise NotImplementedError

    @abstractmethod
    async def set_group_cache(self, group_item: "Group", ttl: int = 21600) -> None:
        """Сохранение группы в кэш"""
        raise NotImplementedError

    @abstractmethod
    async def delete_group_cache(self, group_keys: Iterable[str]) -> None:
        """Удаление группы из кэша"""
        raise NotImplementedError

    @abstractmethod
    async def get_all_groups_cache(self) -> list["Group"]:
        """Получение всех групп из кэша"""
        raise NotImplementedError

    @abstractmethod
    async def set_all_groups_cache(
        self, group_items: Iterable["Group"], ttl: int = 21600
    ) -> None:
        """Сохранение всех групп в кэш"""
        raise NotImplementedError

    @abstractmethod
    async def delete_all_groups_cache(self) -> None:
        """Удаление всех групп из кэша"""
        raise NotImplementedError

    @abstractmethod
    async def get_cabinet_cache(self, cabinet_number: str) -> "Cabinet":
        """Получение кабинета из кэша"""
        raise NotImplementedError

    @abstractmethod
    async def set_cabinet_cache(
        self, cabinet_item: "Cabinet", ttl: int = 604800
    ) -> None:
        """Сохранение группы в кэш"""
        raise NotImplementedError

    @abstractmethod
    async def delete_cabinet_cache(self, cabinet_keys: Iterable[str]) -> None:
        """Удаление кабинета из кэша"""
        raise NotImplementedError

    @abstractmethod
    async def get_all_cabinets_cache(self) -> list["Cabinet"]:
        """Получение всех кабинетов из кэша"""
        raise NotImplementedError

    @abstractmethod
    async def set_all_cabinets_cache(
        self, cabinet_items: Iterable["Cabinet"], ttl: int = 604800
    ) -> None:
        """Сохранение всех кабинетов в кэш"""
        raise NotImplementedError

    @abstractmethod
    async def delete_all_cabinets_cache(self) -> None:
        """Удаление всех кабинетов из кэша"""
        raise NotImplementedError

    @abstractmethod
    async def get_group_day_schedule(
        self, schedule_to: Literal["today", "tomorrow"], group_number: str
    ) -> "GroupDaySchedule":
        """Получение расписания для группы из кэша"""
        raise NotImplementedError

    @abstractmethod
    async def set_group_day_schedule(
        self,
        schedule_to: Literal["today", "tomorrow"],
        day_schedule: "GroupDaySchedule",
    ) -> None:
        """Сохранение расписания для группы в кэш"""
        raise NotImplementedError

    @abstractmethod
    async def delete_group_day_schedule_cache(
        self, items: dict[Literal["today", "tomorrow"], Iterable[str]]
    ) -> None:
        """Удаление расписания для групп из кэша"""
        raise NotImplementedError

    @abstractmethod
    async def get_cabinet_day_schedule(
        self, cabinet_number: str, schedule_to: Literal["today", "tomorrow"]
    ) -> "CabinetDaySchedule":
        """Получение расписания для кабинета из кэша"""
        raise NotImplementedError

    @abstractmethod
    async def set_cabinet_day_schedule(
        self,
        schedule_to: Literal["today", "tomorrow"],
        day_schedule: "CabinetDaySchedule",
    ) -> None:
        """Сохранение расписания для кабинета в кэш"""
        raise NotImplementedError

    @abstractmethod
    async def delete_cabinet_day_schedule_cache(
        self, items: dict[Literal["today", "tomorrow"], Iterable[str]]
    ) -> None:
        """Удаление расписания для кабинетов из кэша"""
        raise NotImplementedError
