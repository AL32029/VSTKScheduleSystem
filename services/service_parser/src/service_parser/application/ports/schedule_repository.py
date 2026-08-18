from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import date
from typing import Literal

from service_parser.domain.entities import Cabinet, DaySchedule, Group


class ScheduleRepository(ABC):
    @abstractmethod
    async def save(
        self, schedules: Iterable["DaySchedule"], dates: date | tuple[date, date]
    ) -> dict[
        date,
        dict[
            Literal["group", "cabinet"],
            dict[Literal["new", "update", "remove"], set["Group | Cabinet"]],
        ],
    ]:
        """Сохранение расписания для групп"""
        raise NotImplementedError
