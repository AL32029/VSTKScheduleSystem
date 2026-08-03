from service_api.infrastructure.pydantic_items.schemas import ScheduleItemSchema
from tests.test_contains import _CABINET_ITEM, _CABINET_ITEMS


# ====================== [ТЕСТЫ ЭНДПОИНТОВ КАБИНЕТОВ] ======================
async def test_get_cabinet_by_number_endpoint(client):
    """Тест должен выполнить HTTP запрос и получить JSON кабинетов"""
    resp = await client.get(f'/cabinets/{_CABINET_ITEM!s}')

    assert resp.status_code == 200

    cabinet = ScheduleItemSchema.model_validate(resp.json()).to_domain('cabinet')

    assert cabinet == _CABINET_ITEM


async def test_get_all_cabinets_endpoint(client):
    """Тест должен выполнить HTTP запрос и получить JSON всех кабинетов"""
    resp = await client.get('/cabinets/')

    assert resp.status_code == 200

    cabinets = [*{ScheduleItemSchema.model_validate(cabinet)
                  for cabinet in resp.json()}]

    assert len(cabinets) == len(_CABINET_ITEMS)
