from dataclasses import dataclass


@dataclass(frozen=True)
class ScheduleItem:
    index: str
    number: str

    def __str__(self) -> str:
        return self.number

    def __eq__(self, other) -> bool:
        if type(self) is not type(other):
            return NotImplemented

        return self.index == other.index

    def __hash__(self) -> int:
        return hash(self.index)


@dataclass(frozen=True)
class Cabinet(ScheduleItem):
    """Сущность кабинета"""


@dataclass(frozen=True)
class Group(ScheduleItem):
    """Сущность группы"""
