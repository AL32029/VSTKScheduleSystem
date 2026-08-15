import datetime
from itertools import chain

import pytest

from service_parser.domain.entities import Cabinet, DaySchedule, Group, Lesson
from service_parser.domain.exceptions import (
    DayScheduleNotFoundError,
    GroupNotFoundError,
)

# ===================== [СУЩНОСТИ ДЛЯ ТЕСТОВ] =====================
_GROUP_NUMBER = "ЖБИ-21"
_GROUP_ITEM = Group(_GROUP_NUMBER)

_SCHEDULE_DATE = datetime.date(2099, 12, 31)
_SCHEDULE_DATES = [
    datetime.date(2099, 12, 1) + datetime.timedelta(days=i) for i in range(5)
]

_SCHEDULE_LESSON_TO_REPLACE_VALUES = [
    (datetime.time(9, 0), datetime.time(9, 45), "Биология", (Cabinet("12к"),)),
    (datetime.time(9, 55), datetime.time(10, 40), "Математика", (Cabinet("42к"),)),
    (datetime.time(10, 50), datetime.time(11, 35), " Рус. лит. ", (Cabinet("31"),)),
    (datetime.time(11, 45), datetime.time(12, 30), "Физкультура", (Cabinet("сз3"),)),
]
_SCHEDULE_LESSON_VALUES = [
    (datetime.time(9, 0), datetime.time(9, 45), "Математика", (Cabinet("42к"),)),
    (datetime.time(9, 55), datetime.time(10, 40), "Биология", (Cabinet("12к"),)),
    (datetime.time(10, 50), datetime.time(11, 35), " Физкультура ", (Cabinet("сз3"),)),
    (datetime.time(11, 45), datetime.time(12, 30), "Рус. лит.", (Cabinet("31"),)),
]

_SCHEDULE_LESSON_TO_REPLACE_ITEMS = [
    Lesson(start, end, name, cabinets)
    for start, end, name, cabinets in _SCHEDULE_LESSON_TO_REPLACE_VALUES
]
_SCHEDULE_LESSON_ITEMS = [
    Lesson(start, end, name, cabinets)
    for start, end, name, cabinets in _SCHEDULE_LESSON_VALUES
]

_DAY_SCHEDULE_TO_REPLACE = DaySchedule.from_existing(
    _SCHEDULE_DATE, _GROUP_NUMBER, _SCHEDULE_LESSON_TO_REPLACE_ITEMS
)
_DAY_SCHEDULE = DaySchedule.from_existing(
    _SCHEDULE_DATE, _GROUP_NUMBER, _SCHEDULE_LESSON_ITEMS
)


# ===================== [ТЕСТЫ МЕТОДА SAVE] =====================
async def test_save_schedule(
    sqlalchemy_group_repo, sqlalchemy_cabinet_repo, sqlalchemy_schedule_repo
):
    """Тест должен корректно сохранить сущность DaySchedule в базу данных"""
    await sqlalchemy_group_repo.save([_GROUP_ITEM])
    await sqlalchemy_cabinet_repo.save(
        {
            cabinet
            for lesson in _SCHEDULE_LESSON_ITEMS
            if lesson.cabinets
            for cabinet in lesson.cabinets
        }
    )

    await sqlalchemy_schedule_repo.save([_DAY_SCHEDULE])

    day_schedule = await sqlalchemy_schedule_repo.get_by_group(
        _GROUP_ITEM, _SCHEDULE_DATE
    )

    assert day_schedule is not None
    assert day_schedule.date == _SCHEDULE_DATE
    assert day_schedule.group.number == _GROUP_NUMBER
    assert day_schedule.lessons == tuple(_SCHEDULE_LESSON_ITEMS)


async def test_save_schedule_with_rewrite(
    sqlalchemy_group_repo, sqlalchemy_cabinet_repo, sqlalchemy_schedule_repo
):
    """
    Тест должен корректно сохранить сущность DaySchedule в базу данных
    с удалением лишних записей
    """
    await sqlalchemy_group_repo.save([_GROUP_ITEM])
    await sqlalchemy_cabinet_repo.save(
        {
            cabinet
            for lesson in chain.from_iterable(
                [_SCHEDULE_LESSON_ITEMS, _SCHEDULE_LESSON_TO_REPLACE_ITEMS]
            )
            if lesson.cabinets
            for cabinet in lesson.cabinets
        }
    )

    await sqlalchemy_schedule_repo.save([_DAY_SCHEDULE])

    await sqlalchemy_schedule_repo.save([_DAY_SCHEDULE_TO_REPLACE])

    day_schedule = await sqlalchemy_schedule_repo.get_by_group(
        _GROUP_ITEM, _SCHEDULE_DATE
    )

    assert day_schedule is not None
    assert day_schedule.date == _SCHEDULE_DATE
    assert day_schedule.group.number == _GROUP_NUMBER
    assert day_schedule.lessons == tuple(_SCHEDULE_LESSON_TO_REPLACE_ITEMS)


async def test_save_schedule_error_group_missing(sqlalchemy_schedule_repo):
    """Тест должен выдать ошибку GroupNotFound"""
    with pytest.raises(GroupNotFoundError) as exc_info:
        await sqlalchemy_schedule_repo.save([_DAY_SCHEDULE])

    assert exc_info.value.args[0] == (
        f"The following groups are missing: "
        f"{', '.join(str(group) for group in [_DAY_SCHEDULE.group])}"
    )


# ===================== [ТЕСТЫ МЕТОДА GET_BY_GROUP] =====================
async def test_get_by_group_error_group_not_found(sqlalchemy_schedule_repo):
    """Тест должен выдать ошибку GroupNotFound"""
    with pytest.raises(GroupNotFoundError) as exc_info:
        await sqlalchemy_schedule_repo.get_by_group(_GROUP_ITEM, _SCHEDULE_DATE)

    assert exc_info.value.args[0] == f"Group {str(_GROUP_ITEM)!r} not found"


async def test_get_by_group_error_day_schedule_not_found(
    sqlalchemy_group_repo, sqlalchemy_schedule_repo
):
    """Тест должен выдать ошибку DayScheduleNotFound"""
    await sqlalchemy_group_repo.save([_GROUP_ITEM])

    with pytest.raises(DayScheduleNotFoundError) as exc_info:
        await sqlalchemy_schedule_repo.get_by_group(_GROUP_ITEM, _SCHEDULE_DATE)

    assert (
        exc_info.value.args[0] == f"Day schedule at {_SCHEDULE_DATE!s} "
        f"for group {str(_GROUP_ITEM)!r} not found"
    )


# ===================== [ТЕСТЫ МЕТОДА GET_MANY_BY_GROUP] =====================
async def test_get_many_by_groups(
    sqlalchemy_group_repo, sqlalchemy_cabinet_repo, sqlalchemy_schedule_repo
):
    """Тест должен корректно получать список DaySchedule за 5 дней"""
    await sqlalchemy_group_repo.save([_GROUP_ITEM])
    await sqlalchemy_cabinet_repo.save(
        {
            cabinet
            for lesson in _SCHEDULE_LESSON_ITEMS
            if lesson.cabinets
            for cabinet in lesson.cabinets
        }
    )
    await sqlalchemy_schedule_repo.save(
        [
            DaySchedule.from_existing(
                schedule_date, _GROUP_ITEM, _SCHEDULE_LESSON_ITEMS
            )
            for schedule_date in _SCHEDULE_DATES
        ]
    )

    day_schedules = await sqlalchemy_schedule_repo.get_many_by_groups(
        [(_GROUP_ITEM, schedule_date) for schedule_date in _SCHEDULE_DATES]
    )

    assert day_schedules
    assert len(list(day_schedules)) == 5
    assert all(
        isinstance(day_schedule, DaySchedule) and day_schedule.group == _GROUP_ITEM
        for day_schedule in day_schedules
    )
    assert all(day_schedule.date in _SCHEDULE_DATES for day_schedule in day_schedules)
    assert all(
        day_schedule.lessons == tuple(_SCHEDULE_LESSON_ITEMS)
        for day_schedule in day_schedules
    )


async def test_get_many_by_groups_error_group_missing(sqlalchemy_schedule_repo):
    """Тест должен выдать ошибку GroupNotFound"""
    with pytest.raises(GroupNotFoundError) as exc_info:
        await sqlalchemy_schedule_repo.get_many_by_groups(
            [(_GROUP_ITEM, schedule_date) for schedule_date in _SCHEDULE_DATES]
        )

    assert exc_info.value.args[0] == (
        f"The following groups are missing: "
        f"{', '.join(str(group) for group in [_GROUP_ITEM])}"
    )
