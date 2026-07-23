import pytest

from service_parser.domain.entities import Group
from service_parser.domain.exceptions.parser_exceptions import ScheduleGroupNotFound


async def test_group_saving(group_repository, group_item):
    await group_repository.save(group_item)

    group = await group_repository.get_by_index(group_item.index)

    assert group is not None
    assert isinstance(group, Group)
    assert group == group_item


async def test_group_deletion(group_repository, group_item_saved):
    await group_repository.delete(group_item_saved)

    with pytest.raises(ScheduleGroupNotFound) as exc_info:
        await group_repository.get_by_index(group_item_saved.index)

    assert exc_info.value.args[0] == f'Group with index {str(group_item_saved.index)!r} not found'


async def test_group_get_by_index(group_repository, group_item_saved):
    group = await group_repository.get_by_index(group_item_saved.index)

    assert group is not None
    assert group == group_item_saved


async def test_group_get_by_index_not_found(group_repository, group_item):
    with pytest.raises(ScheduleGroupNotFound) as exc_info:
        await group_repository.get_by_index(group_item.index)

    assert exc_info.value.args[0] == f'Group with index {str(group_item.index)!r} not found'


async def test_group_get_all(group_repository, group_item_saved):
    groups = await group_repository.get_all()

    assert groups is not None
    assert len(groups) == 1
    assert groups[0] == group_item_saved
