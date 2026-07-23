import pytest

from service_parser.domain.entities import Group
from service_parser.domain.exceptions.parser_exceptions import ScheduleGroupNotFound


@pytest.mark.parametrize('group_number', [
    'ЖБИ-21', 'ОС-21', 'ПЭС-215'
])
async def test_create_group_use_case(group_repository, create_group_use_case, group_number):
    group = await create_group_use_case.execute(group_number)

    assert group is not None
    assert isinstance(group, Group)
    assert group.number == group_number
    assert group.index is not None

    group_db = await group_repository.get_by_index(group_index=group.index)

    assert group_db is not None
    assert group_db == group


@pytest.mark.parametrize('group_number', [
    'ЖБИ-21', 'ОС-21', 'ПЭС-215'
])
async def test_delete_group_use_case(group_repository, create_group_use_case, delete_group_use_case, group_number):
    group = await create_group_use_case.execute(group_number)

    await delete_group_use_case.execute(group_number)

    with pytest.raises(ScheduleGroupNotFound) as exc_info:
        await group_repository.get_by_index(group_index=group.index)

    assert exc_info.value.args[0] == f'Group with index {str(group.index)!r} not found'


@pytest.mark.parametrize('group_number', [
    'ЖБИ-21', 'ОС-21', 'ПЭС-215'
])
async def test_delete_group_use_case_not_found(delete_group_use_case, group_number):
    with pytest.raises(ScheduleGroupNotFound) as exc_info:
        await delete_group_use_case.execute(group_number)

    assert exc_info.value.args[0] == f'Group {group_number!r} not found'


@pytest.mark.parametrize('group_number', [
    'ЖБИ-21', 'ОС-21', 'ПЭС-215'
])
async def test_get_group_by_index_use_case(create_group_use_case, get_group_by_index_use_case, group_number):
    saved_group = await create_group_use_case.execute(group_number)

    group = await get_group_by_index_use_case.execute(saved_group)

    assert group is not None
    assert group.number == group_number
    assert saved_group == group


@pytest.mark.parametrize('group_number', [
    'ЖБИ-21', 'ОС-21', 'ПЭС-215'
])
async def test_get_group_by_index_use_case_not_found(get_group_by_index_use_case, group_number):
    with pytest.raises(ScheduleGroupNotFound) as exc_info:
        await get_group_by_index_use_case.execute(group_number)

    assert exc_info.value.args[0] == f'Group with index {str(Group(group_number).index)!r} not found'


@pytest.mark.parametrize('group_numbers', [
    ['ЖБИ-21', 'ОС-21', 'ПЭС-215']
])
async def test_get_all_groups_use_case(create_group_use_case, get_all_groups_use_case, group_numbers):
    for group in group_numbers:
        await create_group_use_case.execute(group)

    groups = sorted(await get_all_groups_use_case.execute(), key=lambda x: x.index)
    group_numbers = sorted(group_numbers, key=lambda x: Group(x).index)

    assert all(isinstance(group, Group) for group in groups)
    assert len(list(groups)) == len(group_numbers)
    assert all(group == Group(group_number) for group, group_number in zip(groups, group_numbers))
