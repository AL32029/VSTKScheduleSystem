import datetime
from abc import ABC, abstractmethod
from typing import Literal

from service_api.domain.entities import (
    Cabinet,
    CabinetDaySchedule,
    Group,
    GroupDaySchedule,
)


class ScheduleRepository(ABC):
    @abstractmethod
    async def get_schedule_date(self, schedule_type: Literal['today', 'tomorrow']) -> datetime.date:
        """Получение даты расписания"""
        raise NotImplementedError

    @abstractmethod
    async def get_by_group(self, group: 'Group', schedule_date: datetime.date,
                           redirect: bool = True) -> 'GroupDaySchedule':
        """Получение расписания по группе"""
        raise NotImplementedError

    @abstractmethod
    async def get_by_cabinet(self, cabinet: 'Cabinet', schedule_date: datetime.date,
                             redirect: bool = True) -> 'CabinetDaySchedule':
        """Получение расписания по кабинету"""
        raise NotImplementedError
