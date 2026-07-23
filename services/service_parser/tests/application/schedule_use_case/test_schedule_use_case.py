import datetime
from itertools import chain

import pytest

from service_parser.domain.entities import Group, Lesson, Cabinet, DaySchedule
from service_parser.domain.exceptions.parser_exceptions import ScheduleGroupNotFound, DayScheduleNotFound


@pytest.mark.parametrize('group,date,lessons', [
    [Group('ЖБИ-21'), datetime.date(2026, 7, 20), [
        Lesson(datetime.time(9, 0), datetime.time(9, 45), 'Физкультура', (Cabinet('сз3'),)),
        Lesson(datetime.time(9, 55), datetime.time(10, 40), 'Биология', (Cabinet('12к'),)),
        Lesson(datetime.time(10, 50), datetime.time(11, 35), 'Тех. мех', (Cabinet('315'),)),
        Lesson(datetime.time(11, 45), datetime.time(12, 30), 'ОТСМ', (Cabinet('11'),)),
    ]],
])
async def test_create_day_schedule_use_case(group_repository, cabinet_repository, create_day_schedule_use_case,
                                            group, date, lessons):
    await group_repository.save(group)
    for cabinet in chain.from_iterable({lesson.cabinets for lesson in lessons if lesson.cabinets}):
        await cabinet_repository.save(cabinet)

    day_schedule = await create_day_schedule_use_case.execute(group, date, lessons)

    assert day_schedule is not None

    assert isinstance(day_schedule.group, Group)
    assert isinstance(day_schedule.date, datetime.date)

    assert day_schedule.lessons
    assert len(day_schedule.lessons) == len(lessons)
    assert all(isinstance(lesson, Lesson) for lesson in day_schedule.lessons)


@pytest.mark.parametrize('group,date,lessons', [
    [Group('ЖБИ-21'), datetime.date(2026, 7, 20), [
        Lesson(datetime.time(9, 0), datetime.time(9, 45), 'Физкультура', (Cabinet('сз3'),)),
        Lesson(datetime.time(9, 55), datetime.time(10, 40), 'Биология', (Cabinet('12к'),)),
        Lesson(datetime.time(10, 50), datetime.time(11, 35), 'Тех. мех', (Cabinet('315'),)),
        Lesson(datetime.time(11, 45), datetime.time(12, 30), 'ОТСМ', (Cabinet('11'),)),
    ]],
])
async def test_get_day_schedule_by_group_use_case(group_repository, cabinet_repository, create_day_schedule_use_case,
                                                  get_day_schedule_by_group_use_case, group, date, lessons):
    await group_repository.save(group)
    for cabinet in chain.from_iterable({lesson.cabinets for lesson in lessons if lesson.cabinets}):
        await cabinet_repository.save(cabinet)

    day_schedule_saved = await create_day_schedule_use_case.execute(group, date, lessons)

    day_schedule = await get_day_schedule_by_group_use_case.execute(group, date)

    assert day_schedule == day_schedule_saved


@pytest.mark.parametrize('group,date,lessons', [
    [Group('ЖБИ-21'), datetime.date(2026, 7, 20), [
        Lesson(datetime.time(9, 0), datetime.time(9, 45), 'Физкультура', (Cabinet('сз3'),)),
        Lesson(datetime.time(9, 55), datetime.time(10, 40), 'Биология', (Cabinet('12к'),)),
        Lesson(datetime.time(10, 50), datetime.time(11, 35), 'Тех. мех', (Cabinet('315'),)),
        Lesson(datetime.time(11, 45), datetime.time(12, 30), 'ОТСМ', (Cabinet('11'),)),
    ]],
])
async def test_get_day_schedule_by_group_use_case_without_save(group_repository, cabinet_repository,
                                                               create_day_schedule_use_case,
                                                               get_day_schedule_by_group_use_case, group,
                                                               date, lessons):
    with pytest.raises(ScheduleGroupNotFound) as exc_info:
        await get_day_schedule_by_group_use_case.execute(group, date)

    assert exc_info.value.args[0] == f'Group {str(group)!r} not found'

    await group_repository.save(group)

    with pytest.raises(DayScheduleNotFound) as exc_info:
        await get_day_schedule_by_group_use_case.execute(group, date)

    assert exc_info.value.args[0] == f'Day schedule at {str(date)} for group {str(group)!r} not found'
