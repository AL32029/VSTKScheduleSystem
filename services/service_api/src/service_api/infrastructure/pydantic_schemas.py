import datetime
from collections.abc import Iterable
from typing import Literal, cast

from pydantic import BaseModel, computed_field

from service_api.domain.entities import (
    _IGNORED_LESSONS,
    Cabinet,
    CabinetDaySchedule,
    CabinetLesson,
    Group,
    GroupDaySchedule,
    GroupLesson,
)


class APISchemas(BaseModel):
    """Базовая модель схем API"""


class ResponseSchema[T: "APISchemas"](BaseModel):
    """Модель схемы успешного ответа API"""

    success: bool = True
    data: T | Iterable[T]


class ScheduleItemSchema(APISchemas):
    index: str
    number: str

    def to_domain(self, domain_type: Literal["group", "cabinet"]) -> "Group | Cabinet":
        if domain_type == "group":
            return Group(**self.model_dump(mode="json"))
        else:
            return Cabinet(**self.model_dump(mode="json"))

    def __hash__(self):
        return hash(self.index)


class GroupLessonSchema(APISchemas):
    start: datetime.time
    end: datetime.time

    name: str

    cabinets: Iterable["ScheduleItemSchema"]

    def to_domain(self) -> "GroupLesson":
        return GroupLesson(
            start=self.start,
            end=self.end,
            name=self.name,
            cabinets=[cast("Cabinet", x.to_domain("cabinet")) for x in self.cabinets],
        )

    def __hash__(self):
        return hash((self.start, self.end, self.name, tuple(self.cabinets)))


class CabinetLessonSchema(APISchemas):
    start: datetime.time
    end: datetime.time

    group: "ScheduleItemSchema"

    name: str

    cabinets: Iterable["ScheduleItemSchema"]

    def to_domain(self) -> "CabinetLesson":
        return CabinetLesson(
            start=self.start,
            end=self.end,
            group=cast("Group", self.group.to_domain("group")),
            name=self.name,
            cabinets=[cast("Cabinet", x.to_domain("cabinet")) for x in self.cabinets],
        )

    def __hash__(self):
        return hash((self.start, self.end, self.group, self.name, tuple(self.cabinets)))


class GroupDayScheduleSchema(APISchemas):
    group: "ScheduleItemSchema"

    date: datetime.date

    lessons: Iterable["GroupLessonSchema"]

    @computed_field
    @property
    def lessons_count(self) -> int:
        return len(
            [
                lesson
                for lesson in self.lessons
                if lesson.name.strip().lower() not in _IGNORED_LESSONS
            ]
        )

    @computed_field
    @property
    def pairs_count(self) -> float:
        return self.lessons_count / 2

    def to_domain(self) -> "GroupDaySchedule":
        return GroupDaySchedule(
            group=cast(Group, self.group.to_domain("group")),
            date=self.date,
            lessons=[lesson.to_domain() for lesson in self.lessons],
        )

    def __hash__(self):
        return hash(
            (
                self.group,
                self.date,
                tuple(self.lessons),
                self.lessons_count,
                self.pairs_count,
            )
        )


class CabinetDayScheduleSchema(APISchemas):
    cabinet: "ScheduleItemSchema"

    date: datetime.date

    lessons: Iterable["CabinetLessonSchema"]

    @computed_field
    @property
    def lessons_count(self) -> int:
        return len(
            [
                lesson
                for lesson in self.lessons
                if lesson.name.strip().lower() not in _IGNORED_LESSONS
            ]
        )

    @computed_field
    @property
    def pairs_count(self) -> float:
        return self.lessons_count / 2

    def to_domain(self) -> "CabinetDaySchedule":
        return CabinetDaySchedule(
            cabinet=cast(Cabinet, self.cabinet.to_domain("cabinet")),
            date=self.date,
            lessons=[lesson.to_domain() for lesson in self.lessons],
        )

    def __hash__(self):
        return hash(
            (
                self.cabinet,
                self.date,
                tuple(self.lessons),
                self.lessons_count,
                self.pairs_count,
            )
        )
