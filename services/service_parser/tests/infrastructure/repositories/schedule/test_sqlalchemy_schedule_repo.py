import pytest

from service_parser.domain.entities import Lesson, DaySchedule
from service_parser.domain.exceptions.parser_exceptions import ScheduleGroupNotFound, ScheduleCabinetNotFound, \
    DayScheduleNotFound


async def test_day_schedule_saving(schedule_repository, day_schedule_with_pre_saved):
    await schedule_repository.save(day_schedule_with_pre_saved)

    day_schedule = await schedule_repository.get_by_group(day_schedule_with_pre_saved.group,
                                                          day_schedule_with_pre_saved.date)

    assert day_schedule is not None
    assert day_schedule.group == day_schedule_with_pre_saved.group
    assert day_schedule.date == day_schedule_with_pre_saved.date
    assert day_schedule.lessons
    assert all(isinstance(lesson, Lesson) for lesson in day_schedule.lessons)
    assert len(day_schedule.lessons) == 6


async def test_day_schedule_saving_error_group_not_found(schedule_repository, day_schedule_item):
    with pytest.raises(ScheduleGroupNotFound) as exc_info:
        await schedule_repository.save(day_schedule_item)

    assert exc_info.value.args[0] == f'Group {str(day_schedule_item.group)!r} not found'


async def test_day_schedule_saving_error_cabinets_not_found(group_repository, schedule_repository, day_schedule_item):
    await group_repository.save(day_schedule_item.group)

    with pytest.raises(ScheduleCabinetNotFound) as exc_info:
        await schedule_repository.save(day_schedule_item)

    lesson = day_schedule_item.lessons[0]
    cabinets_missing = {*lesson.cabinets}

    assert exc_info.value.args[0] == (f'The following classrooms are missing for the {lesson.name!r} (№1) '
                                      f'pair: {', '.join([str(cab) for cab in cabinets_missing])}')


async def test_day_schedule_many_saving(schedule_repository, day_schedule_with_pre_saved):
    await schedule_repository.save_all([day_schedule_with_pre_saved])

    day_schedule = await schedule_repository.get_by_group(day_schedule_with_pre_saved.group,
                                                          day_schedule_with_pre_saved.date)

    assert day_schedule is not None
    assert day_schedule.group == day_schedule_with_pre_saved.group
    assert day_schedule.date == day_schedule_with_pre_saved.date
    assert day_schedule.lessons
    assert all(isinstance(lesson, Lesson) for lesson in day_schedule.lessons)
    assert len(day_schedule.lessons) == 6


async def test_day_schedule_get_by_group(schedule_repository, day_schedule_item_saved):
    day_schedule = await schedule_repository.get_by_group(day_schedule_item_saved.group, day_schedule_item_saved.date)

    assert day_schedule is not None
    assert isinstance(day_schedule, DaySchedule)
    assert day_schedule == day_schedule_item_saved
    assert day_schedule.lessons
    assert day_schedule.lessons == day_schedule_item_saved.lessons
    assert all(isinstance(lesson, Lesson) for lesson in day_schedule.lessons)


async def test_day_schedule_get_by_group_without_saving_schedule(group_repository, schedule_repository,
                                                                 day_schedule_item):
    with pytest.raises(ScheduleGroupNotFound) as exc_info:
        await schedule_repository.get_by_group(day_schedule_item.group, day_schedule_item.date)

    assert exc_info.value.args[0] == f'Group {str(day_schedule_item.group)!r} not found'

    await group_repository.save(day_schedule_item.group)

    with pytest.raises(DayScheduleNotFound) as exc_info:
        await schedule_repository.get_by_group(day_schedule_item.group, day_schedule_item.date)

    assert exc_info.value.args[0] == (f'Day schedule at {str(day_schedule_item.date)} for group '
                                      f'{str(day_schedule_item.group)!r} not found')
