from dataclasses import asdict

import pytest

from service_bot.domain.exceptions import (
    CabinetNotFound,
    GroupNotFound,
    ScheduleDateNotFound,
    ScheduleForCabinetNotFound,
    ScheduleForGroupNotFound,
)
from tests.test_contains import _CABINET_DAY_SCHEDULE, _GROUP_DAY_SCHEDULE


async def test_get_group_day_schedule(httpx_mock, client, httpx_schedule_repository):
    httpx_mock.add_response(
        method='GET',
        url=f'{client.base_url}/schedule/group',
        match_params={
            'group_number': _GROUP_DAY_SCHEDULE.schedule_item.number,
            'schedule_to': 'tomorrow',

        },
        json={
            "group": asdict(_GROUP_DAY_SCHEDULE.schedule_item),
            "date": _GROUP_DAY_SCHEDULE.date.isoformat(),
            "lessons": [
                {
                    "start": lesson.start.isoformat(),
                    "end": lesson.end.isoformat(),
                    "name": lesson.name,
                    "cabinets": [asdict(cabinet) for cabinet in lesson.cabinets]
                }
                for lesson in sorted(_GROUP_DAY_SCHEDULE.lessons, key=lambda x: x.start)
            ],
            "lessons_count": _GROUP_DAY_SCHEDULE.lessons_count,
            "pairs_count": _GROUP_DAY_SCHEDULE.pairs_count
        }
    )

    schedule = await httpx_schedule_repository.get_day_schedule(_GROUP_DAY_SCHEDULE.schedule_item.number,
                                                                'tomorrow', 'group')

    assert schedule == _GROUP_DAY_SCHEDULE


async def test_get_group_day_schedule_error_group_not_found(httpx_mock, client, httpx_schedule_repository):
    httpx_mock.add_response(
        method='GET',
        url=f'{client.base_url}/schedule/group',
        match_params={
            'group_number': _GROUP_DAY_SCHEDULE.schedule_item.number,
            'schedule_to': 'tomorrow',

        },
        status_code=404,
        content=f'Group with number {_GROUP_DAY_SCHEDULE.schedule_item.number!r} not found'
    )

    with pytest.raises(GroupNotFound) as exc_info:
        await httpx_schedule_repository.get_day_schedule(_GROUP_DAY_SCHEDULE.schedule_item.number,
                                                         'tomorrow', 'group')

    assert exc_info.value.args[0] == f'Группа {_GROUP_DAY_SCHEDULE.schedule_item.number} не найдена'


async def test_get_cabinet_day_schedule_error_cabinet_not_found(httpx_mock, client, httpx_schedule_repository):
    httpx_mock.add_response(
        method='GET',
        url=f'{client.base_url}/schedule/cabinet',
        match_params={
            'cabinet_number': _CABINET_DAY_SCHEDULE.schedule_item.number,
            'schedule_to': 'tomorrow',

        },
        status_code=404,
        content=f'Cabinet with number {_CABINET_DAY_SCHEDULE.schedule_item.number!r} not found'
    )

    with pytest.raises(CabinetNotFound) as exc_info:
        await httpx_schedule_repository.get_day_schedule(_CABINET_DAY_SCHEDULE.schedule_item.number,
                                                         'tomorrow', 'cabinet')

    assert exc_info.value.args[0] == f'Кабинет {_CABINET_DAY_SCHEDULE.schedule_item.number} не найден'


async def test_get_day_schedule_error_schedule_date_not_found(httpx_mock, client, httpx_schedule_repository):
    httpx_mock.add_response(
        method='GET',
        url=f'{client.base_url}/schedule/group',
        match_params={
            'group_number': _GROUP_DAY_SCHEDULE.schedule_item.number,
            'schedule_to': 'tomorrow',

        },
        status_code=404,
        content='The database does not contain a schedule date for tomorrow'
    )

    with pytest.raises(ScheduleDateNotFound) as exc_info:
        await httpx_schedule_repository.get_day_schedule(_GROUP_DAY_SCHEDULE.schedule_item.number,
                                                         'tomorrow', 'group')

    assert exc_info.value.args[0] == 'Расписание на завтра еще не было опубликовано'

async def test_get_group_day_schedule_error_schedule_date_not_found(httpx_mock, client, httpx_schedule_repository):
    httpx_mock.add_response(
        method='GET',
        url=f'{client.base_url}/schedule/group',
        match_params={
            'group_number': _GROUP_DAY_SCHEDULE.schedule_item.number,
            'schedule_to': 'tomorrow',

        },
        status_code=404,
        content=f'The database does not contain a schedule date for '
                f'{_GROUP_DAY_SCHEDULE.schedule_item.number} for tomorrow'
    )

    with pytest.raises(ScheduleForGroupNotFound) as exc_info:
        await httpx_schedule_repository.get_day_schedule(_GROUP_DAY_SCHEDULE.schedule_item.number,
                                                         'tomorrow', 'group')

    assert exc_info.value.args[0] == 'У группы нет пар на завтра'

async def test_get_cabinet_day_schedule_error_schedule_date_not_found(httpx_mock, client, httpx_schedule_repository):
    httpx_mock.add_response(
        method='GET',
        url=f'{client.base_url}/schedule/cabinet',
        match_params={
            'cabinet_number': _CABINET_DAY_SCHEDULE.schedule_item.number,
            'schedule_to': 'tomorrow',

        },
        status_code=404,
        content=f'The database does not contain a schedule date for '
                f'{_CABINET_DAY_SCHEDULE.schedule_item.number} for tomorrow'
    )

    with pytest.raises(ScheduleForCabinetNotFound) as exc_info:
        await httpx_schedule_repository.get_day_schedule(_CABINET_DAY_SCHEDULE.schedule_item.number,
                                                         'tomorrow', 'cabinet')

    assert exc_info.value.args[0] == 'В кабинете отсутствуют пары на завтра'
