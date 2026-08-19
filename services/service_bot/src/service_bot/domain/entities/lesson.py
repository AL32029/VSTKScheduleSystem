import datetime
from collections.abc import Iterable
from dataclasses import dataclass

from .schedule_items import Cabinet, Group


@dataclass
class Lesson:
    """Сущность пары (для группы)"""

    start: datetime.time
    end: datetime.time

    name: str

    cabinets: Iterable["Cabinet"]

    def __post_init__(self):
        if not isinstance(self.cabinets, list):
            self.cabinets = list(self.cabinets)


@dataclass
class CabinetLesson(Lesson):
    """Сущность пары (для кабинета)"""

    group: "Group"
