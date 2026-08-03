from service_api.infrastructure.pydantic_items import (
    CabinetDayScheduleSchema,
    GroupDayScheduleSchema,
)
from tests.test_contains import _CABINET_DAY_SCHEDULE_ITEM, _GROUP_DAY_SCHEDULE_ITEM


# ====================== [ТЕСТЫ ЭНДПОИНТОВ РАСПИСАНИЯ] ======================
async def test_get_group_day_schedule_endpoint(client):
    """Тест должен выполнить HTTP запрос и получить JSON расписания для группы"""
    resp = await client.get('/schedule/group', params={
        'group_number': _GROUP_DAY_SCHEDULE_ITEM.group.number,
        'schedule_to': 'tomorrow'
    })

    assert resp.status_code == 200

    assert GroupDayScheduleSchema.model_validate(resp.json()).to_domain() == _GROUP_DAY_SCHEDULE_ITEM


async def test_get_cabinet_day_schedule_endpoint(client):
    """Тест должен выполнить HTTP запрос и получить JSON расписания для кабинета"""
    resp = await client.get('/schedule/cabinet', params={
        'cabinet_number': _CABINET_DAY_SCHEDULE_ITEM.cabinet.number,
        'schedule_to': 'tomorrow'
    })

    assert resp.status_code == 200

    assert CabinetDayScheduleSchema.model_validate(resp.json()).to_domain() == _CABINET_DAY_SCHEDULE_ITEM
