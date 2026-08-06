import datetime
from abc import ABC, abstractmethod
from collections.abc import Iterable

from service_parser.domain.entities import DaySchedule, Group


class ScheduleRepository(ABC):
    @abstractmethod
    async def save(self, day_schedule: Iterable['DaySchedule']) -> None:
        """Сохранение расписания для групп"""
        raise NotImplementedError

    @abstractmethod
    async def get_by_group(self, group: 'Group', date: datetime.date) -> 'DaySchedule':
        """Получение расписания пар для группы"""
        raise NotImplementedError

    @abstractmethod
    async def get_many_by_groups(self, items: Iterable[tuple['Group', datetime.date]]) -> set['DaySchedule']:
        """Получение нескольких расписаний пар для групп"""
        raise NotImplementedError
