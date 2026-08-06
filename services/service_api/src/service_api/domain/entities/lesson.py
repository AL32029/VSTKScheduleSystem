import datetime
from collections.abc import Iterable
from dataclasses import dataclass

from .cabinet import Cabinet
from .group import Group


@dataclass(frozen=True)
class GroupLesson:
    start: datetime.time
    end: datetime.time

    name: str

    cabinets: Iterable['Cabinet']

    def __hash__(self):
        return hash((self.start, self.end, self.name, tuple(self.cabinets)))

    def __eq__(self, other):
        if not isinstance(other, GroupLesson):
            raise NotImplementedError

        return (self.start, self.end, self.name, tuple(self.cabinets)) == (other.start, other.end,
                                                                           other.name, tuple(other.cabinets))


@dataclass(frozen=True)
class CabinetLesson:
    start: datetime.time
    end: datetime.time

    group: 'Group'

    name: str

    cabinets: Iterable['Cabinet']

    def __hash__(self):
        return hash((self.start, self.end, self.name, tuple(self.cabinets)))

    def __eq__(self, other):
        if not isinstance(other, CabinetLesson):
            raise NotImplementedError

        return (self.start, self.end, self.name, tuple(self.cabinets)) == (other.start, other.end,
                                                                           other.name, tuple(other.cabinets))
