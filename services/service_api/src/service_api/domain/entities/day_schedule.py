import datetime
from collections.abc import Iterable
from dataclasses import dataclass

from service_api.domain.exceptions import DayScheduleEmptyLessonsError

from .cabinet import Cabinet
from .group import Group
from .lesson import CabinetLesson, GroupLesson

_IGNORED_LESSONS = (
    'обед', 'каникулы',
)


@dataclass(frozen=True)
class GroupDaySchedule:
    group: 'Group'

    date: datetime.date

    lessons: 'Iterable[GroupLesson]'

    @property
    def lessons_count(self) -> int:
        return len([lesson
                    for lesson in self.lessons
                    if lesson.name.strip().lower() not in _IGNORED_LESSONS])

    @property
    def pairs_count(self) -> float:
        return self.lessons_count / 2

    def __hash__(self):
        return hash((self.group, self.date, tuple(self.lessons)))

    def __eq__(self, other):
        if not isinstance(other, GroupDaySchedule):
            raise NotImplementedError

        return (self.group, self.date, self.lessons) == (other.group, other.date, tuple(other.lessons))

    def __post_init__(self):
        if not self.lessons:
            raise DayScheduleEmptyLessonsError('Day schedule cannot have an empty schedule')

        object.__setattr__(self, 'lessons', tuple(sorted(self.lessons, key=lambda x: x.start)))


@dataclass(frozen=True)
class CabinetDaySchedule:
    cabinet: 'Cabinet'

    date: datetime.date

    lessons: 'Iterable[CabinetLesson]'

    @property
    def lessons_count(self) -> int:
        return len([lesson
                    for lesson in self.lessons
                    if lesson.name.strip().lower() not in _IGNORED_LESSONS])

    @property
    def pairs_count(self) -> float:
        return self.lessons_count / 2

    def __hash__(self):
        return hash((self.cabinet, self.date, tuple(self.lessons)))

    def __eq__(self, other):
        if not isinstance(other, CabinetDaySchedule):
            raise NotImplementedError

        return (self.cabinet, self.date, self.lessons) == (other.cabinet, other.date, tuple(other.lessons))

    def __post_init__(self):
        if not self.lessons:
            raise DayScheduleEmptyLessonsError('Day schedule cannot have an empty schedule')

        object.__setattr__(self, 'lessons', tuple(sorted(self.lessons, key=lambda x: x.start)))
