from service_bot.domain.entities import (
    Cabinet,
    CabinetLesson,
    DaySchedule,
    Group,
    Lesson,
)
from tests.test_contains import (
    _CABINET_LESSON_VALUES,
    _CABINET_NUMBERS,
    _GROUP_NUMBERS,
    _LESSON_VALUES,
    _SCHEDULE_DATE,
)


# ====================== [ТЕСТЫ СУЩНОСТИ DAYSCHEDULE (для группы)] =====================
def test_group_day_schedule_creation():
    group_item = Group(_GROUP_NUMBERS[0][0], _GROUP_NUMBERS[0][1])
    lessons = [
        Lesson(start, end, name, (Cabinet(x[0], x[1]) for x in cabinets))
        for start, end, name, cabinets in _LESSON_VALUES
    ]

    day_schedule = DaySchedule(_SCHEDULE_DATE, group_item, lessons)

    assert isinstance(day_schedule.schedule_item, Group)
    assert isinstance(day_schedule.lessons, list)
    assert all(isinstance(lesson, Lesson) for lesson in lessons)
    assert day_schedule.lessons == sorted(day_schedule.lessons, key=lambda x: x.start)
    assert day_schedule.lessons_count == len(_LESSON_VALUES)
    assert day_schedule.pairs_count == day_schedule.lessons_count / 2


# ===================== [ТЕСТЫ СУЩНОСТИ DAYSCHEDULE (для кабинета)] ===================
def test_cabinet_day_schedule_creation():
    cabinet_item = Cabinet(_CABINET_NUMBERS[0][0], _CABINET_NUMBERS[0][1])
    lessons = [
        CabinetLesson(
            start=start,
            end=end,
            group=group,
            name=name,
            cabinets=(Cabinet(x[0], x[1]) for x in cabinets),
        )
        for start, end, group, name, cabinets in _CABINET_LESSON_VALUES
    ]

    day_schedule = DaySchedule(_SCHEDULE_DATE, cabinet_item, lessons)

    assert isinstance(day_schedule.schedule_item, Cabinet)
    assert isinstance(day_schedule.lessons, list)
    assert all(isinstance(lesson, CabinetLesson) for lesson in lessons)
    assert day_schedule.lessons == sorted(day_schedule.lessons, key=lambda x: x.start)
    assert day_schedule.lessons_count == len(_CABINET_LESSON_VALUES)
    assert day_schedule.pairs_count == day_schedule.lessons_count / 2
