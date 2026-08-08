from dataclasses import asdict

import pytest

from service_bot.domain.entities import Group
from service_bot.domain.exceptions import GroupNotFound
from tests.test_contains import _GROUP_ITEMS


@pytest.mark.parametrize('group', _GROUP_ITEMS)
async def test_get_by_number(httpx_mock, client, httpx_group_repository, group):
    httpx_mock.add_response(
        method='GET',
        url=f'{client.base_url}/groups/{group.number}',
        json=asdict(group)
    )

    group_item = await httpx_group_repository.get_by_number(group.number)

    assert isinstance(group_item, Group)
    assert group_item == group


@pytest.mark.parametrize('group', _GROUP_ITEMS)
async def test_get_by_number_not_found(httpx_mock, client, httpx_group_repository, group):
    group_number = str(group)

    httpx_mock.add_response(
        method='GET',
        url=f'{client.base_url}/groups/{group_number}',
        status_code=404,
        content=f'Group with number {group_number!r} not found'
    )

    with pytest.raises(GroupNotFound) as exc_info:
        await httpx_group_repository.get_by_number(group_number)

    assert exc_info.value.args[0] == f'Группа {group_number} не найдена'


async def test_get_all(httpx_mock, client, httpx_group_repository):
    httpx_mock.add_response(
        method='GET',
        url=f'{client.base_url}/groups/',
        json=[asdict(group) for group in sorted(_GROUP_ITEMS, key=lambda x: x.index)]
    )

    group_items = await httpx_group_repository.get_all()

    assert group_items
    assert isinstance(group_items, list)
    assert len(group_items) == len(_GROUP_ITEMS)
    assert all(isinstance(group, Group) for group in sorted(group_items, key=lambda x: x.index))
