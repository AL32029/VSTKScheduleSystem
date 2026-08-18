from abc import ABC, abstractmethod
from datetime import date

from service_parser.domain.entities import DaySchedule, Group


class ScheduleProvider(ABC):
    @abstractmethod
    async def get_schedule_for_groups(
        self,
    ) -> tuple[dict[Group, DaySchedule], date | tuple[date, date]]:
        """Получение расписания по URL"""
        raise NotImplementedError
