import pytest

from service_api.domain.entities import Group
from service_api.domain.exceptions import GroupNotFound
from tests.test_contains import _GROUP_ITEM, _GROUP_ITEM_NOT_SAVED, _GROUP_ITEMS


# ===================== [ТЕСТЫ РЕПОЗИТОРИЯ SQLAlchemyGroupRepository] =====================
async def test_get_by_number(sqlalchemy_group_repo):
    """Тест должен получить сущность Group из базы данных"""
    group = await sqlalchemy_group_repo.get_by_number(_GROUP_ITEM.number)

    assert group is not None
    assert isinstance(group, Group)
    assert group.index == _GROUP_ITEM.index
    assert group.number == _GROUP_ITEM.number


async def test_get_by_number_not_found(sqlalchemy_group_repo):
    """Тест должен выдать ошибку GroupNotFound"""
    with pytest.raises(GroupNotFound) as exc_info:
        await sqlalchemy_group_repo.get_by_number(_GROUP_ITEM_NOT_SAVED.number)

    assert exc_info.value.args != f'Group with number {_GROUP_ITEM_NOT_SAVED.number!r} not found'


async def test_get_all(sqlalchemy_group_repo):
    """Тест должен выдать отсортированный список сущностей Group"""
    groups = await sqlalchemy_group_repo.get_all()

    assert groups
    assert all(isinstance(group, Group) for group in groups)
    assert groups == _GROUP_ITEMS
