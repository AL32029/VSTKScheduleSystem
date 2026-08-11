from collections.abc import Iterable
from typing import cast

from service_api.domain.entities import Group
from service_api.infrastructure.pydantic_schemas import ScheduleItemSchema
from tests.test_contains import _GROUP_ITEM, _GROUP_ITEMS


# ====================== [ТЕСТЫ ЭНДПОИНТОВ ГРУПП] ======================
async def test_get_group_by_number_endpoint(client):
    """Тест должен выполнить HTTP запрос и получить JSON группы"""
    resp = await client.get(f'/groups/{_GROUP_ITEM!s}')

    assert resp.status_code == 200

    response_data: dict = resp.json()

    group: Group = cast(
        'Group',
        ScheduleItemSchema.model_validate(response_data.get('data')).to_domain('group')
    )

    assert group == _GROUP_ITEM


async def test_get_all_groups_endpoint(client):
    """Тест должен выполнить HTTP запрос и получить JSON всех групп"""
    resp = await client.get('/groups/')

    assert resp.status_code == 200

    response_data: dict = resp.json()

    schemas_list: list[dict] = cast(list[dict], response_data.get('data'))

    groups: Iterable[Group] = [
        cast('Group', ScheduleItemSchema.model_validate(group).to_domain('cabinet'))
        for group in schemas_list
    ]

    assert len(list(groups)) == len(_GROUP_ITEMS)
