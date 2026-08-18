from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import date

from service_parser.domain.entities import DaySchedule


class ScheduleRepository(ABC):
    @abstractmethod
    async def save(
        self, schedules: Iterable["DaySchedule"], dates: date | tuple[date, date]
    ):
        """Сохранение расписания для групп"""
        raise NotImplementedError
