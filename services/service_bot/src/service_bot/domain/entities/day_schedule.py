import datetime
from dataclasses import dataclass

from service_bot.domain.exceptions import InvalidDayScheduleLessonType

from .cabinet import Cabinet
from .group import Group
from .lesson import CabinetLesson, Lesson


@dataclass
class DaySchedule:
    """Сущность расписания для кабинета/группы на конкретную дату"""

    date: datetime.date

    schedule_item: "Group | Cabinet"

    lessons: list["Lesson | CabinetLesson"]

    @property
    def lessons_count(self) -> int:
        """Количество уроков"""
        return len(self.lessons)

    @property
    def pairs_count(self) -> float | int:
        """Количество пар [float для нечетного количества/int для четного количества]"""
        count = self.lessons_count / 2

        if self.lessons_count % 2 == 0:
            return int(count)

        return count

    def __post_init__(self):
        if isinstance(self.schedule_item, Group) and not all(
            type(lesson) is Lesson for lesson in self.lessons
        ):
            raise InvalidDayScheduleLessonType(
                "Lessons should only accept objects of type Lesson when "
                "the type of lessons is Group"
            )
        elif isinstance(self.schedule_item, Cabinet) and not all(
            type(lesson) is CabinetLesson for lesson in self.lessons
        ):
            raise InvalidDayScheduleLessonType(
                "Lessons should only accept objects of type CabinetLesson when "
                "the type of lessons is Cabinet"
            )

        self.lessons = sorted(self.lessons, key=lambda x: x.start)
