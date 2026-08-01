import datetime
from collections.abc import Iterable

from pydantic import BaseModel


class ScheduleItemResponse(BaseModel):
    index: str
    number: str


class GroupLessonResponse(BaseModel):
    start: datetime.time
    end: datetime.time

    name: str

    cabinets: Iterable[ScheduleItemResponse]


class CabinetLessonResponse(BaseModel):
    start: datetime.time
    end: datetime.time

    group: ScheduleItemResponse

    name: str

    cabinets: Iterable[ScheduleItemResponse]


class GroupDayScheduleResponse(BaseModel):
    group: ScheduleItemResponse

    date: datetime.date

    lessons: Iterable[GroupLessonResponse]

    lessons_count: int
    pairs_count: float


class CabinetDayScheduleResponse(BaseModel):
    cabinet: ScheduleItemResponse

    date: datetime.date

    lessons: Iterable[CabinetLessonResponse]

    lessons_count: int
    pairs_count: float
