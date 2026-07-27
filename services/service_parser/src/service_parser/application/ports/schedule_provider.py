from abc import ABC, abstractmethod

from service_parser.domain.entities import Group
from service_parser.domain.entities.lesson import DaySchedule


class ScheduleProvider(ABC):
    @abstractmethod
    async def get_schedule_for_groups(self) -> dict[Group, list[DaySchedule]]:
        """Получение расписания по URL"""
        raise NotImplementedError