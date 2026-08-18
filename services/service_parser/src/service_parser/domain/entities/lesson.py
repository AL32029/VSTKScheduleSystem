from collections.abc import Iterable
from dataclasses import dataclass
from datetime import time

from service_parser.domain.entities import Cabinet, Group
from service_parser.domain.exceptions import (
    LessonEmptyNameError,
    LessonEndTimeError,
    LessonOverlapError,
)


@dataclass(frozen=True)
class Lesson:
    start: time
    end: time

    name: str
    cabinets: tuple["Cabinet", ...] = ()

    id: int | None = None

    def __post_init__(self):
        if self.end < self.start:
            raise LessonEndTimeError(
                f"End time {str(self.end)!r} should be "
                f"greater than start time {str(self.start)!r}"
            )

        if not self.name.strip():
            raise LessonEmptyNameError("Lesson name is missing")

        if self.name != self.name.strip():
            object.__setattr__(self, "name", self.name.strip())

    def __hash__(self):
        return hash((self.start, self.end, self.name, self.cabinets))


class DaySchedule:
    def __init__(self, group: "str | Group"):
        self._group = group if isinstance(group, Group) else Group(group)
        self._lessons: list[Lesson] = []

    @classmethod
    def from_existing(
        cls, group: "str | Group", lessons: Iterable["Lesson"]
    ) -> "DaySchedule":
        instance = cls(group if isinstance(group, Group) else Group(group))
        for lesson in lessons:
            instance._add_lesson_internal(lesson)
        return instance

    def add_lesson(
        self,
        start: time,
        end: time,
        name: str,
        cabinets: Iterable["Cabinet"] | None = None,
        lesson_id: int | None = None,
    ) -> Lesson:
        cabinets_tuple = tuple(cab for cab in (cabinets or ()))
        new_lesson = Lesson(start, end, name, cabinets_tuple, lesson_id)

        self._ensure_no_overlap(new_lesson)

        self._lessons.append(new_lesson)
        return new_lesson

    @property
    def group(self) -> "Group":
        return self._group

    @property
    def lessons(self) -> tuple["Lesson", ...]:
        return tuple(self._lessons)

    def _ensure_no_overlap(self, new_lesson: "Lesson") -> None:
        for existing in self._lessons:
            if self._is_overlap(existing, new_lesson):
                raise LessonOverlapError(
                    f"The lesson overlaps with the lesson {existing.name!r} "
                    f"({existing.start!s} - {existing.end!s})"
                )

    @staticmethod
    def _is_overlap(a: "Lesson", b: "Lesson") -> bool:
        return a.start < b.end and b.start < a.end

    def _add_lesson_internal(self, lesson: "Lesson") -> None:
        self._ensure_no_overlap(lesson)
        self._lessons.append(lesson)

    def __eq__(self, other):
        if not isinstance(other, DaySchedule):
            raise NotImplementedError

        return (self.group, self.lessons) == (
            other.group,
            other.lessons,
        )

    def __hash__(self):
        return hash((self.group, self.lessons))
