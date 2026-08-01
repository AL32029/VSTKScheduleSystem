import pytest

from service_api.domain.entities import (
    CabinetDaySchedule,
    CabinetLesson,
    GroupDaySchedule,
    GroupLesson,
)
from service_api.domain.exceptions import DayScheduleEmptyLessonsError
from tests.test_contains import (
    _CABINET_ITEM,
    _CABINET_LESSON_ITEMS,
    _DAY_SCHEDULE_DATE,
    _GROUP_ITEM,
    _GROUP_LESSON_ITEMS,
)


# ====================== [ТЕСТЫ СУЩНОСТИ GroupDaySchedule] ======================
def test_create_group_day_schedule():
    """Тест должен корректно создавать сущность GroupDatSchedule"""
    day_schedule = GroupDaySchedule(_GROUP_ITEM, _DAY_SCHEDULE_DATE, _GROUP_LESSON_ITEMS)

    assert day_schedule.group == _GROUP_ITEM
    assert day_schedule.date == _DAY_SCHEDULE_DATE
    assert day_schedule.lessons
    assert len(list(day_schedule.lessons)) == len(_GROUP_LESSON_ITEMS)
    assert all(isinstance(lesson, GroupLesson) for lesson in day_schedule.lessons)
    assert day_schedule.lessons == tuple(sorted(_GROUP_LESSON_ITEMS, key=lambda x: x.start))


def test_create_group_day_schedule_with_empty_lessons():
    """Тест должен выдать ошибку DayScheduleEmptyLessonsError"""
    with pytest.raises(DayScheduleEmptyLessonsError) as exc_info:
        GroupDaySchedule(_GROUP_ITEM, _DAY_SCHEDULE_DATE, {})

    assert exc_info.value.args[0] == 'Day schedule cannot have an empty schedule'


def test_group_day_schedule_equal():
    """Тест должен проверить равенство двух равных сущностей GroupDatSchedule"""

    first_day_schedule = GroupDaySchedule(_GROUP_ITEM, _DAY_SCHEDULE_DATE, _GROUP_LESSON_ITEMS)
    second_day_schedule = GroupDaySchedule(_GROUP_ITEM, _DAY_SCHEDULE_DATE, _GROUP_LESSON_ITEMS)

    assert first_day_schedule == second_day_schedule


def test_group_day_schedule_equal_hash():
    """Тест должен проверить равенство хэша двух равных сущностей GroupDatSchedule"""

    first_day_schedule = GroupDaySchedule(_GROUP_ITEM, _DAY_SCHEDULE_DATE, _GROUP_LESSON_ITEMS)
    second_day_schedule = GroupDaySchedule(_GROUP_ITEM, _DAY_SCHEDULE_DATE, _GROUP_LESSON_ITEMS)

    assert hash(first_day_schedule) == hash(second_day_schedule)


# ====================== [ТЕСТЫ СУЩНОСТИ CabinetDaySchedule] ======================
def test_create_cabinet_day_schedule():
    """Тест должен корректно создавать сущность CabinetDaySchedule"""
    day_schedule = CabinetDaySchedule(_CABINET_ITEM, _DAY_SCHEDULE_DATE, _CABINET_LESSON_ITEMS)

    assert day_schedule.cabinet == _CABINET_ITEM
    assert day_schedule.date == _DAY_SCHEDULE_DATE
    assert day_schedule.lessons
    assert len(list(day_schedule.lessons)) == len(_CABINET_LESSON_ITEMS)
    assert all(isinstance(lesson, CabinetLesson) for lesson in day_schedule.lessons)
    assert day_schedule.lessons == tuple(sorted(_CABINET_LESSON_ITEMS, key=lambda x: x.start))


def test_create_cabinet_day_schedule_with_empty_lessons():
    """Тест должен выдать ошибку DayScheduleEmptyLessonsError"""
    with pytest.raises(DayScheduleEmptyLessonsError) as exc_info:
        CabinetDaySchedule(_CABINET_ITEM, _DAY_SCHEDULE_DATE, {})

    assert exc_info.value.args[0] == 'Day schedule cannot have an empty schedule'


def test_cabinet_day_schedule_equal():
    """Тест должен проверить равенство двух равных сущностей CabinetDaySchedule"""

    first_day_schedule = CabinetDaySchedule(_CABINET_ITEM, _DAY_SCHEDULE_DATE, _CABINET_LESSON_ITEMS)
    second_day_schedule = CabinetDaySchedule(_CABINET_ITEM, _DAY_SCHEDULE_DATE, _CABINET_LESSON_ITEMS)

    assert first_day_schedule == second_day_schedule


def test_cabinet_day_schedule_equal_hash():
    """Тест должен проверить равенство хэша двух равных сущностей CabinetDaySchedule"""

    first_day_schedule = CabinetDaySchedule(_CABINET_ITEM, _DAY_SCHEDULE_DATE, _CABINET_LESSON_ITEMS)
    second_day_schedule = CabinetDaySchedule(_CABINET_ITEM, _DAY_SCHEDULE_DATE, _CABINET_LESSON_ITEMS)

    assert hash(first_day_schedule) == hash(second_day_schedule)
