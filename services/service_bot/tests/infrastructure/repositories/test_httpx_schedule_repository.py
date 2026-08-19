import datetime
from dataclasses import asdict

import pytest

from service_bot.domain.exceptions import (
    CabinetNotFoundError,
    GroupNotFoundError,
    ScheduleDateNotFoundError,
    ScheduleForCabinetNotFoundError,
    ScheduleForGroupNotFoundError,
)
from tests.test_contains import _CABINET_DAY_SCHEDULE, _GROUP_DAY_SCHEDULE


async def test_get_group_day_schedule(httpx_mock, client, httpx_schedule_repository):
    httpx_mock.add_response(
        method="GET",
        url=f"{client.base_url}/schedule/group",
        match_params={
            "group_number": _GROUP_DAY_SCHEDULE.schedule_item.number,
            "schedule_to": "tomorrow",
            "grouping_lessons": "false",
        },
        json={
            "success": True,
            "data": {
                "group": asdict(_GROUP_DAY_SCHEDULE.schedule_item),
                "date": _GROUP_DAY_SCHEDULE.date.isoformat(),
                "lessons": [
                    {
                        "start": lesson.start.isoformat(),
                        "end": lesson.end.isoformat(),
                        "name": lesson.name,
                        "cabinets": [asdict(cabinet) for cabinet in lesson.cabinets],
                    }
                    for lesson in sorted(
                        _GROUP_DAY_SCHEDULE.lessons,
                        key=lambda x: x.start,
                    )
                ],
                "lessons_count": _GROUP_DAY_SCHEDULE.lessons_count,
                "pairs_count": _GROUP_DAY_SCHEDULE.pairs_count,
            },
        },
    )

    schedule = await httpx_schedule_repository.get_day_schedule(
        _GROUP_DAY_SCHEDULE.schedule_item.number, "tomorrow", "group", False
    )

    assert schedule == _GROUP_DAY_SCHEDULE


async def test_get_group_day_schedule_error_group_not_found(
    httpx_mock,
    client,
    httpx_schedule_repository,
):
    httpx_mock.add_response(
        method="GET",
        url=f"{client.base_url}/schedule/group",
        match_params={
            "group_number": _GROUP_DAY_SCHEDULE.schedule_item.number,
            "schedule_to": "tomorrow",
            "grouping_lessons": "false",
        },
        status_code=404,
        json={
            "success": False,
            "error": {
                "code": "GROUP_NOT_FOUND",
                "detail": f"Group with number "
                f"{_GROUP_DAY_SCHEDULE.schedule_item.number!r} not found",
                "extra": {"input_number": _GROUP_DAY_SCHEDULE.schedule_item.number},
            },
        },
    )

    with pytest.raises(GroupNotFoundError) as exc_info:
        await httpx_schedule_repository.get_day_schedule(
            _GROUP_DAY_SCHEDULE.schedule_item.number, "tomorrow", "group", False
        )

    assert exc_info.value.args[0] == str(
        GroupNotFoundError(_GROUP_DAY_SCHEDULE.schedule_item.number),
    )


async def test_get_cabinet_day_schedule_error_cabinet_not_found(
    httpx_mock,
    client,
    httpx_schedule_repository,
):
    httpx_mock.add_response(
        method="GET",
        url=f"{client.base_url}/schedule/cabinet",
        match_params={
            "cabinet_number": _CABINET_DAY_SCHEDULE.schedule_item.number,
            "schedule_to": "tomorrow",
            "grouping_lessons": "false",
        },
        status_code=404,
        json={
            "success": False,
            "error": {
                "code": "CABINET_NOT_FOUND",
                "detail": f"Cabinet with number "
                f"{_CABINET_DAY_SCHEDULE.schedule_item.number!r} not found",
                "extra": {"input_number": _CABINET_DAY_SCHEDULE.schedule_item.number},
            },
        },
    )

    with pytest.raises(CabinetNotFoundError) as exc_info:
        await httpx_schedule_repository.get_day_schedule(
            _CABINET_DAY_SCHEDULE.schedule_item.number, "tomorrow", "cabinet", False
        )

    assert exc_info.value.args[0] == str(
        CabinetNotFoundError(_CABINET_DAY_SCHEDULE.schedule_item.number),
    )


async def test_get_day_schedule_error_schedule_date_not_found(
    httpx_mock,
    client,
    httpx_schedule_repository,
):
    httpx_mock.add_response(
        method="GET",
        url=f"{client.base_url}/schedule/group",
        match_params={
            "group_number": _GROUP_DAY_SCHEDULE.schedule_item.number,
            "schedule_to": "tomorrow",
            "grouping_lessons": "false",
        },
        status_code=404,
        json={
            "success": False,
            "error": {
                "code": "SCHEDULE_DATE_NOT_FOUND",
                "detail": "The schedule for tomorrow has not been published",
                "extra": {"schedule_to": "tomorrow"},
            },
        },
    )

    with pytest.raises(ScheduleDateNotFoundError) as exc_info:
        await httpx_schedule_repository.get_day_schedule(
            _GROUP_DAY_SCHEDULE.schedule_item.number, "tomorrow", "group", False
        )

    assert exc_info.value.args[0] == str(ScheduleDateNotFoundError("tomorrow"))


async def test_get_group_day_schedule_error_schedule_date_not_found(
    httpx_mock,
    client,
    httpx_schedule_repository,
):
    httpx_mock.add_response(
        method="GET",
        url=f"{client.base_url}/schedule/group",
        match_params={
            "group_number": _GROUP_DAY_SCHEDULE.schedule_item.number,
            "schedule_to": "tomorrow",
            "grouping_lessons": "false",
        },
        status_code=404,
        json={
            "success": False,
            "error": {
                "code": "SCHEDULE_FOR_GROUP_NOT_FOUND",
                "detail": f"For the {_GROUP_DAY_SCHEDULE.schedule_item!s} group, "
                f"there are no lessons scheduled for "
                f"tomorrow (2099-12-31)",
                "extra": {
                    "item": asdict(_GROUP_DAY_SCHEDULE.schedule_item),
                    "schedule_to": "tomorrow",
                    "schedule_date": "2099-12-31",
                },
            },
        },
    )

    with pytest.raises(ScheduleForGroupNotFoundError) as exc_info:
        await httpx_schedule_repository.get_day_schedule(
            _GROUP_DAY_SCHEDULE.schedule_item.number, "tomorrow", "group", False
        )

    assert exc_info.value.args[0] == str(
        ScheduleForGroupNotFoundError(
            _GROUP_DAY_SCHEDULE.schedule_item,
            "tomorrow",
            datetime.date(2099, 12, 31),
        ),
    )


async def test_get_cabinet_day_schedule_error_schedule_date_not_found(
    httpx_mock,
    client,
    httpx_schedule_repository,
):
    httpx_mock.add_response(
        method="GET",
        url=f"{client.base_url}/schedule/cabinet",
        match_params={
            "cabinet_number": _CABINET_DAY_SCHEDULE.schedule_item.number,
            "schedule_to": "tomorrow",
            "grouping_lessons": "false",
        },
        status_code=404,
        json={
            "success": False,
            "error": {
                "code": "SCHEDULE_FOR_CABINET_NOT_FOUND",
                "detail": f"For the {_CABINET_DAY_SCHEDULE.schedule_item!s} cabinet, "
                f"there are no lessons scheduled for "
                f"tomorrow (2099-12-31)",
                "extra": {
                    "item": asdict(_CABINET_DAY_SCHEDULE.schedule_item),
                    "schedule_to": "tomorrow",
                    "schedule_date": "2099-12-31",
                },
            },
        },
    )

    with pytest.raises(ScheduleForCabinetNotFoundError) as exc_info:
        await httpx_schedule_repository.get_day_schedule(
            _CABINET_DAY_SCHEDULE.schedule_item.number, "tomorrow", "cabinet", False
        )

    assert exc_info.value.args[0] == str(
        ScheduleForCabinetNotFoundError(
            _CABINET_DAY_SCHEDULE.schedule_item,
            "tomorrow",
            datetime.date(2099, 12, 31),
        ),
    )
