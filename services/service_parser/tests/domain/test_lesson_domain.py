import datetime
import datetime as dt

import pytest

from service_parser.domain.entities import Cabinet, DaySchedule, Group, Lesson
from service_parser.domain.exceptions import (
    LessonEmptyNameError,
    LessonEndTimeError,
    LessonOverlapError,
)

# ====================== [ВАЛИДНЫЕ ЗНАЧЕНИЯ] ======================
_LESSON_VALUES = [
    (dt.time(9, 0), dt.time(9, 45), "Математика", (Cabinet("42к"),)),
    (
        dt.time(9, 55),
        dt.time(11, 35),
        " Мех. оборудование ",
        (Cabinet("упм. 1, л. 6"),),
    ),
    (dt.time(11, 45), dt.time(12, 30), "Информатика", (Cabinet("310"), Cabinet("212"))),
]
_LESSON_PAIRS = [
    Lesson(start, end, name, cabinets)
    for (start, end, name, cabinets) in _LESSON_VALUES
]

_GROUP_NUMBER = "ЖБИ-21"
_DAY_SCHEDULE_DATE = datetime.date(2030, 9, 12)
_OVERLAPPING_LESSON_PAIRS = [
    (
        Lesson(dt.time(9, 0), dt.time(9, 45), "Математика", ()),
        Lesson(dt.time(8, 50), dt.time(9, 20), "Пересекается", ()),
    ),
    (
        Lesson(dt.time(9, 0), dt.time(9, 45), "Математика", ()),
        Lesson(dt.time(9, 30), dt.time(10, 0), "Пересекается", ()),
    ),
    (
        Lesson(dt.time(9, 0), dt.time(9, 45), "Математика", ()),
        Lesson(dt.time(9, 10), dt.time(9, 30), "Пересекается", ()),
    ),
    (
        Lesson(dt.time(9, 0), dt.time(9, 45), "Математика", ()),
        Lesson(dt.time(8, 50), dt.time(10, 0), "Пересекается", ()),
    ),
]
_NON_OVERLAPPING_LESSON_PAIRS = [
    (
        Lesson(dt.time(9, 0), dt.time(9, 45), "Математика", ()),
        Lesson(dt.time(8, 0), dt.time(8, 45), "Не пересекается", ()),
    ),
    (
        Lesson(dt.time(9, 0), dt.time(9, 45), "Математика", ()),
        Lesson(dt.time(10, 0), dt.time(10, 45), "Не пересекается", ()),
    ),
]

# ====================== [НЕВАЛИДНЫЕ ЗНАЧЕНИЯ] ======================
_INVALID_TIMES_LESSON_VALUES = [
    (end, start, name, cabinets) for (start, end, name, cabinets) in _LESSON_VALUES
]
_EMPTY_NAMES_LESSON_VALUES = [
    (start, end, "", cabinets) for (start, end, _, cabinets) in _LESSON_VALUES
]


# ====================== [ТЕСТЫ СУЩНОСТИ LESSON] ======================
@pytest.mark.parametrize(("start", "end", "name", "cabinets"), _LESSON_VALUES)
def test_create_lesson_entity(
    start: dt.time, end: dt.time, name: str, cabinets: tuple[Cabinet, ...]
):
    """Тест должен корректно создать сущность Lesson"""
    lesson = Lesson(start, end, name, cabinets)

    assert lesson.start == start
    assert lesson.end == end
    assert lesson.name == name.strip()
    assert lesson.cabinets == cabinets


@pytest.mark.parametrize(
    ("start", "end", "name", "cabinets"), _INVALID_TIMES_LESSON_VALUES
)
def test_create_lesson_entity_with_invalid_time(
    start: dt.time, end: dt.time, name: str, cabinets: tuple[Cabinet, ...]
):
    """Тест должен выдать ошибку InvalidLessonEndTime"""
    with pytest.raises(LessonEndTimeError) as exc_info:
        Lesson(start, end, name, cabinets)

    assert (
        exc_info.value.args[0]
        == f"End time {str(end)!r} should be greater than start time {str(start)!r}"
    )


@pytest.mark.parametrize(
    ("start", "end", "name", "cabinets"), _EMPTY_NAMES_LESSON_VALUES
)
def test_create_lesson_entity_with_empty_name(
    start: dt.time, end: dt.time, name: str, cabinets: tuple[Cabinet, ...]
):
    """Тест должен выдать ошибку MissingLessonNameError"""
    with pytest.raises(LessonEmptyNameError) as exc_info:
        Lesson(start, end, name, cabinets)

    assert exc_info.value.args[0] == "Lesson name is missing"


@pytest.mark.parametrize(("start", "end", "name", "cabinets"), _LESSON_VALUES)
def test_lesson_entity_equal_hash(
    start: dt.time, end: dt.time, name: str, cabinets: tuple[Cabinet, ...]
):
    """Тест должен проверить равенство хэша двух равных сущностей Lesson"""
    first_lesson = Lesson(start, end, name, cabinets)
    second_lesson = Lesson(start, end, name, cabinets)

    assert hash(first_lesson) == hash(second_lesson)


# ====================== [ТЕСТЫ СУЩНОСТИ DAYSCHEDULE] ======================
def test_create_empty_day_schedule_entity():
    """Тест должен корректно создать сущность DaySchedule без lessons"""
    day_schedule = DaySchedule(_DAY_SCHEDULE_DATE, _GROUP_NUMBER)

    assert day_schedule.date == _DAY_SCHEDULE_DATE
    assert isinstance(day_schedule.group, Group)
    assert not day_schedule.lessons


@pytest.mark.parametrize("lessons", _NON_OVERLAPPING_LESSON_PAIRS)
def test_create_day_schedule_entity(lessons: tuple[Lesson, Lesson]):
    """Тест должен корректно создать сущность DaySchedule с lessons"""
    day_schedule = DaySchedule.from_existing(_DAY_SCHEDULE_DATE, _GROUP_NUMBER, lessons)

    assert day_schedule.date == _DAY_SCHEDULE_DATE
    assert isinstance(day_schedule.group, Group)
    assert day_schedule.lessons
    assert len(day_schedule.lessons) == len(lessons)
    assert all(isinstance(lesson, Lesson) for lesson in day_schedule.lessons)


@pytest.mark.parametrize(("existing_lesson", "new_lesson"), _OVERLAPPING_LESSON_PAIRS)
def test_create_day_schedule_entity_with_overlap_lessons(
    existing_lesson: Lesson, new_lesson: Lesson
):
    """Тест должен выдать ошибку LessonOverlapError"""
    with pytest.raises(LessonOverlapError) as exc_info:
        DaySchedule.from_existing(
            _DAY_SCHEDULE_DATE, _GROUP_NUMBER, (existing_lesson, new_lesson)
        )

    assert exc_info.value.args[0] == (
        f"The lesson overlaps with the lesson {existing_lesson.name!r} "
        f"({existing_lesson.start!s} - {existing_lesson.end!s})"
    )


@pytest.mark.parametrize(("start", "end", "name", "cabinets"), _LESSON_VALUES)
def test_day_schedule_entity_add_lesson(
    start: dt.time, end: dt.time, name: str, cabinets: tuple[Cabinet, ...]
):
    day_schedule = DaySchedule(_DAY_SCHEDULE_DATE, _GROUP_NUMBER)

    day_schedule.add_lesson(start, end, name, cabinets)

    assert day_schedule.lessons
    assert len(day_schedule.lessons) == 1

    lesson = day_schedule.lessons[0]
    assert isinstance(lesson, Lesson)
    assert lesson.start == start
    assert lesson.end == end
    assert lesson.name == name.strip()
    assert lesson.cabinets == cabinets


def test_day_schedule_entity_equal():
    """Тест должен проверить равенство двух равных сущностей DaySchedule"""
    first_day_schedule = DaySchedule.from_existing(
        _DAY_SCHEDULE_DATE, _GROUP_NUMBER, _LESSON_PAIRS
    )
    second_day_schedule = DaySchedule.from_existing(
        _DAY_SCHEDULE_DATE, _GROUP_NUMBER, _LESSON_PAIRS
    )

    assert first_day_schedule == second_day_schedule


def test_day_schedule_entity_equal_hash():
    """Тест должен проверить равенство хэша двух равных сущностей DaySchedule"""
    first_day_schedule = DaySchedule.from_existing(
        _DAY_SCHEDULE_DATE, _GROUP_NUMBER, _LESSON_PAIRS
    )
    second_day_schedule = DaySchedule.from_existing(
        _DAY_SCHEDULE_DATE, _GROUP_NUMBER, _LESSON_PAIRS
    )

    assert hash(first_day_schedule) == hash(second_day_schedule)
