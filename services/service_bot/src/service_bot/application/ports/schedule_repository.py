from abc import ABC, abstractmethod
from typing import Literal

from service_bot.domain.entities.day_schedule import DaySchedule


class ScheduleRepository(ABC):
    @abstractmethod
    async def get_day_schedule(self, schedule_item: str, schedule_to: Literal['today', 'tomorrow'],
                               schedule_for: Literal['group', 'cabinet']) -> 'DaySchedule':
        """Получение расписания"""
        raise NotImplementedError
