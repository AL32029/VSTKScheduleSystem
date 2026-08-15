import datetime
from typing import Literal, cast

from pydantic import BaseModel, Field

from service_bot.domain.entities import (
    Cabinet,
    CabinetLesson,
    DaySchedule,
    Group,
    Lesson,
)


class ScheduleItem(BaseModel):
    """Pydantic-схема группы/кабинета"""

    index: str
    number: str

    def to_domain(self, item_type: Literal["group", "cabinet"]) -> "Group | Cabinet":
        """Конвертация схемы в сущность Group/Cabinet"""
        if item_type == "group":
            return Group(self.index, self.number)
        return Cabinet(self.index, self.number)


class LessonItem(BaseModel):
    """Pydantic-схема урока для DayScheduleItem"""

    start: datetime.time
    end: datetime.time

    group: "ScheduleItem | None" = Field(default=None)
    name: str

    cabinets: list["ScheduleItem"]

    def to_domain(
        self, item_type: Literal["group", "cabinet"],
    ) -> "Lesson | CabinetLesson":
        """Конвертация схемы в сущность Lesson/CabinetLesson"""
        if item_type == "group":
            return Lesson(
                start=self.start,
                end=self.end,
                name=self.name,
                cabinets=cast(
                    "list[Cabinet]", [x.to_domain("cabinet") for x in self.cabinets],
                ),
            )
        return CabinetLesson(
            start=self.start,
            end=self.end,
            group=cast("Group", self.group.to_domain("group")),
            name=self.name,
            cabinets=cast(
                "list[Cabinet]", [x.to_domain("cabinet") for x in self.cabinets],
            ),
        )


class DayScheduleItem(BaseModel):
    """Pydantic-схема расписания пар для группы/кабинета"""

    date: datetime.date

    group: "ScheduleItem | None" = Field(default=None)
    cabinet: "ScheduleItem | None" = Field(default=None)

    lessons: list["LessonItem"]

    def to_domain(self, schedule_type: Literal["group", "cabinet"]) -> "DaySchedule":
        return DaySchedule(
            date=self.date,
            schedule_item=(
                self.group if schedule_type == "group" else self.cabinet
            ).to_domain(schedule_type),
            lessons=[x.to_domain(schedule_type) for x in self.lessons],
        )
