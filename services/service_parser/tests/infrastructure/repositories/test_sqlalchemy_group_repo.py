from collections.abc import Iterable

import pytest
from patterns import ITEM_INDEX

from service_parser.domain.entities import Group
from service_parser.domain.exceptions import GroupNotFound

# ===================== [СУЩНОСТИ ДЛЯ ТЕСТОВ] =====================
_VALID_GROUP_NUMBERS = ["ЖБИ-21", "ОС-21", "ПЭС-215"]
_VALID_GROUP_ITEMS = [Group(group) for group in _VALID_GROUP_NUMBERS]


# ===================== [ТЕСТЫ МЕТОДА SAVE] =====================
@pytest.mark.parametrize("group", _VALID_GROUP_ITEMS)
async def test_save_group(sqlalchemy_group_repo, group):
    """Тест должен корректно сохранить сущность Group в базу данных"""
    await sqlalchemy_group_repo.save([group])

    group_item = await sqlalchemy_group_repo.get_by_index(group.index)

    assert group_item == group


async def test_save_many_groups(sqlalchemy_group_repo):
    """Тест должен корректно сохранить несколько сущностей Group в базу данных"""
    await sqlalchemy_group_repo.save(_VALID_GROUP_ITEMS)

    groups = await sqlalchemy_group_repo.get_all()

    assert groups
    assert len(list(groups)) == len(_VALID_GROUP_ITEMS)


# ===================== [ТЕСТЫ МЕТОДА DELETE] =====================
@pytest.mark.parametrize("group", _VALID_GROUP_ITEMS)
async def test_delete_group(sqlalchemy_group_repo, group):
    """Тест должен корректно удалить сущность Group из базы данных"""
    await sqlalchemy_group_repo.save([group])

    group_item = await sqlalchemy_group_repo.get_by_index(group.index)

    await sqlalchemy_group_repo.delete(group_item)

    with pytest.raises(GroupNotFound):
        await sqlalchemy_group_repo.get_by_index(group.index)


# ===================== [ТЕСТЫ МЕТОДА GET_BY_INDEX] =====================
@pytest.mark.parametrize("group_number", _VALID_GROUP_NUMBERS)
async def test_get_by_index_error_not_found(sqlalchemy_group_repo, group_number):
    """Тест должен выдать ошибку GroupNotFound"""
    group_index = ITEM_INDEX.sub("", group_number)

    with pytest.raises(GroupNotFound) as exc_info:
        await sqlalchemy_group_repo.get_by_index(group_index)

    assert exc_info.value.args[0] == f"Group with index {group_index!r} not found"


# ===================== [ТЕСТЫ МЕТОДА GET_ALL] =====================
async def test_get_all_empty_list(sqlalchemy_group_repo):
    """Тест должен выдать пустой список"""
    groups = await sqlalchemy_group_repo.get_all()

    assert isinstance(groups, Iterable)
    assert not groups
