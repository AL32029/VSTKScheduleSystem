from service_api.presentation.rest.schemas import ScheduleItemResponse
from tests.test_contains import _CABINET_ITEM, _CABINET_ITEMS


# ====================== [ТЕСТЫ ЭНДПОИНТОВ КАБИНЕТОВ] ======================
async def test_get_cabinet_by_number_endpoint(client):
    """Тест должен выполнить HTTP запрос и получить JSON кабинетов"""
    resp = await client.get(f'/cabinets/{_CABINET_ITEM!s}')

    assert resp.status_code == 200

    cabinet = ScheduleItemResponse(**resp.json())

    assert cabinet.index == _CABINET_ITEM.index
    assert cabinet.number == _CABINET_ITEM.number


async def test_get_all_cabinets_endpoint(client):
    """Тест должен выполнить HTTP запрос и получить JSON всех кабинетов"""
    resp = await client.get('/cabinets/')

    assert resp.status_code == 200

    cabinets = {ScheduleItemResponse(**cabinet)
                for cabinet in resp.json()}

    assert len(list(cabinets)) == len(_CABINET_ITEMS)
