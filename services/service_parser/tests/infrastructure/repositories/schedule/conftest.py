import datetime
from itertools import chain

import pytest

from service_parser.domain.entities import DaySchedule, Group, Lesson, Cabinet


@pytest.fixture
def day_schedule_item() -> DaySchedule:
    return DaySchedule.from_existing(
        date=datetime.date(2099, 12, 31),
        group=Group('ЖБИ-21'),
        lessons=[
            Lesson(
                start=datetime.time(9, 0),
                end=datetime.time(9, 45),
                name='Математика',
                cabinets=(Cabinet('42к'),)
            ),
            Lesson(
                start=datetime.time(9, 55),
                end=datetime.time(10, 40),
                name='Математика',
                cabinets=(Cabinet('42к'),)
            ),
            Lesson(
                start=datetime.time(10, 50),
                end=datetime.time(11, 35),
                name='ОТСМ',
                cabinets=(Cabinet('11'),)
            ),
            Lesson(
                start=datetime.time(11, 45),
                end=datetime.time(12, 30),
                name='История ИБ в контексте ВИ',
                cabinets=(Cabinet('43'),)
            ),
            Lesson(
                start=datetime.time(13, 35),
                end=datetime.time(14, 20),
                name='Обед',
                cabinets=tuple()
            ),
            Lesson(
                start=datetime.time(14, 30),
                end=datetime.time(15, 15),
                name='ОТСМ',
                cabinets=(Cabinet('43'),)
            ),
        ]
    )

@pytest.fixture
async def day_schedule_with_pre_saved(group_repository, cabinet_repository, day_schedule_item) -> DaySchedule:
    await group_repository.save(day_schedule_item.group)

    for cabinet in set(chain.from_iterable([lesson.cabinets for lesson in day_schedule_item.lessons if lesson.cabinets])):
        await cabinet_repository.save(cabinet)

    return day_schedule_item


@pytest.fixture
async def day_schedule_item_saved(schedule_repository, day_schedule_with_pre_saved) -> DaySchedule:
    await schedule_repository.save(day_schedule_with_pre_saved)

    return day_schedule_with_pre_saved