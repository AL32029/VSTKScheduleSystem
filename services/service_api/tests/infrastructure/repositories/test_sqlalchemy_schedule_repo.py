import datetime

import pytest

from service_api.domain.entities import CabinetDaySchedule, GroupDaySchedule
from service_api.domain.exceptions import (
    CabinetDayScheduleNotFound,
    GroupDayScheduleNotFound,
    ScheduleDateNotFound,
)
from tests.test_contains import (
    _CABINET_DAY_SCHEDULE_ITEM,
    _CABINET_ITEM,
    _CABINET_ITEM_NOT_SAVED,
    _DAY_SCHEDULE_DATE,
    _GROUP_DAY_SCHEDULE_ITEM,
    _GROUP_ITEM,
)


# ================== [ТЕСТЫ РЕПОЗИТОРИЯ SQLAlchemyScheduleRepository] ==================
async def test_get_schedule_date(sqlalchemy_schedule_repo):
    """Тест должен получить дату расписания (datetime.date) из базы данных"""
    schedule_date = await sqlalchemy_schedule_repo.get_schedule_date("tomorrow")

    assert schedule_date is not None
    assert isinstance(schedule_date, datetime.date)
    assert schedule_date == _DAY_SCHEDULE_DATE


async def test_get_schedule_date_not_found(sqlalchemy_schedule_repo):
    """Тест должен выдать ошибку ScheduleDateNotFound"""
    with pytest.raises(ScheduleDateNotFound) as exc_info:
        await sqlalchemy_schedule_repo.get_schedule_date("today")

    assert exc_info.value.args[0] == str(ScheduleDateNotFound("today"))


async def test_get_by_group(sqlalchemy_schedule_repo):
    """Тест должен получить сущность GroupDaySchedule из базы данных"""
    day_schedule = await sqlalchemy_schedule_repo.get_by_group(
        _GROUP_ITEM, "today", _DAY_SCHEDULE_DATE, redirect=False
    )

    assert day_schedule is not None
    assert isinstance(day_schedule, GroupDaySchedule)
    assert day_schedule == _GROUP_DAY_SCHEDULE_ITEM


async def test_get_by_group_not_found(sqlalchemy_schedule_repo):
    """Тест должен выдать ошибку GroupDayScheduleNotFound"""
    invalid_schedule_date = _DAY_SCHEDULE_DATE + datetime.timedelta(days=1)
    with pytest.raises(GroupDayScheduleNotFound) as exc_info:
        await sqlalchemy_schedule_repo.get_by_group(
            _GROUP_ITEM, "today", invalid_schedule_date, redirect=False
        )

    assert exc_info.value.args[0] == str(
        GroupDayScheduleNotFound(_GROUP_ITEM, "today", invalid_schedule_date)
    )


async def test_get_by_cabinet(sqlalchemy_schedule_repo):
    """Тест должен получить сущность CabinetDaySchedule из базы данных"""
    day_schedule = await sqlalchemy_schedule_repo.get_by_cabinet(
        _CABINET_ITEM, "today", _DAY_SCHEDULE_DATE, redirect=False
    )

    assert day_schedule is not None
    assert isinstance(day_schedule, CabinetDaySchedule)
    assert day_schedule == _CABINET_DAY_SCHEDULE_ITEM


async def test_get_by_cabinet_not_found(sqlalchemy_schedule_repo):
    """Тест должен выдать ошибку CabinetDayScheduleNotFound"""
    invalid_schedule_date = _DAY_SCHEDULE_DATE + datetime.timedelta(days=1)
    with pytest.raises(CabinetDayScheduleNotFound) as exc_info:
        await sqlalchemy_schedule_repo.get_by_cabinet(
            _CABINET_ITEM_NOT_SAVED, "today", invalid_schedule_date, redirect=False
        )

    assert exc_info.value.args[0] == str(
        CabinetDayScheduleNotFound(
            _CABINET_ITEM_NOT_SAVED, "today", invalid_schedule_date
        )
    )
