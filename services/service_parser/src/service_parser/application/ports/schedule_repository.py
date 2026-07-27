import datetime
from abc import ABC, abstractmethod
from typing import Iterable

from service_parser.domain.entities import Group
from service_parser.domain.entities.lesson import DaySchedule


class ScheduleRepository(ABC):
    @abstractmethod
    async def save(self, day_schedule: Iterable[DaySchedule]) -> None:
        """Сохранение расписания для групп"""
        raise NotImplementedError

    @abstractmethod
    async def get_by_group(self, group: Group, date: datetime.date) -> DaySchedule:
        """Получение расписания пар для группы"""
        raise NotImplementedError

    @abstractmethod
    async def get_many_by_groups(self, items: Iterable[tuple[Group, datetime.date]]) -> Iterable[DaySchedule]:
        """Получение нескольких расписаний пар для групп"""
        raise NotImplementedError
