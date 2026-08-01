import datetime
from collections.abc import Iterable

from pydantic import BaseModel


class ScheduleItemResponse(BaseModel):
    index: str
    number: str

    def __hash__(self):
        return hash(self.index)


class GroupLessonResponse(BaseModel):
    start: datetime.time
    end: datetime.time

    name: str

    cabinets: Iterable[ScheduleItemResponse]

    def __hash__(self):
        return hash((self.start, self.end, self.name, tuple(self.cabinets)))


class CabinetLessonResponse(BaseModel):
    start: datetime.time
    end: datetime.time

    group: ScheduleItemResponse

    name: str

    cabinets: Iterable[ScheduleItemResponse]

    def __hash__(self):
        return hash((self.start, self.end, self.group, self.name, tuple(self.cabinets)))


class GroupDayScheduleResponse(BaseModel):
    group: ScheduleItemResponse

    date: datetime.date

    lessons: Iterable[GroupLessonResponse]

    lessons_count: int
    pairs_count: float

    def __hash__(self):
        return hash((self.group, self.date, tuple(self.lessons), self.lessons_count, self.pairs_count))


class CabinetDayScheduleResponse(BaseModel):
    cabinet: ScheduleItemResponse

    date: datetime.date

    lessons: Iterable[CabinetLessonResponse]

    lessons_count: int
    pairs_count: float

    def __hash__(self):
        return hash((self.cabinet, self.date, tuple(self.lessons), self.lessons_count, self.pairs_count))
