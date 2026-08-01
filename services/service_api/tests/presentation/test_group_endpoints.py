from service_api.presentation.rest.schemas import ScheduleItemResponse
from tests.test_contains import _GROUP_ITEM, _GROUP_ITEMS


# ====================== [ТЕСТЫ ЭНДПОИНТОВ ГРУПП] ======================
async def test_get_group_by_number_endpoint(client):
    """Тест должен выполнить HTTP запрос и получить JSON группы"""
    resp = await client.get(f'/groups/{_GROUP_ITEM!s}')

    assert resp.status_code == 200

    group = ScheduleItemResponse(**resp.json())

    assert group.index == _GROUP_ITEM.index
    assert group.number == _GROUP_ITEM.number


async def test_get_all_groups_endpoint(client):
    """Тест должен выполнить HTTP запрос и получить JSON всех групп"""
    resp = await client.get('/groups/')

    assert resp.status_code == 200

    groups = {ScheduleItemResponse(**group)
              for group in resp.json()}

    assert len(list(groups)) == len(_GROUP_ITEMS)
