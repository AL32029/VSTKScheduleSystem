import pytest

from service_api.domain.entities import Group
from service_api.domain.exceptions import GroupNumberFormatError
from service_api.domain.shared.patterns import ITEM_INDEX
from tests.test_contains import (
    _GROUP_ITEMS,
    _INVALID_GROUP_NUMBERS,
    _VALID_GROUP_NUMBERS,
)


# ====================== [ТЕСТЫ СУЩНОСТИ GROUP] ======================
@pytest.mark.parametrize('group_number', _VALID_GROUP_NUMBERS)
def test_create_group_entity(group_number: str):
    """Тест должен корректно создать сущность Group"""
    group = Group(group_number)

    assert group.number == group_number
    assert group.index == ITEM_INDEX.sub('', group_number.lower())


@pytest.mark.parametrize('invalid_group_number', _INVALID_GROUP_NUMBERS)
def test_create_group_entity_with_invalid_number(invalid_group_number: str):
    """Тест должен выдать ошибку GroupNumberFormatError"""
    with pytest.raises(GroupNumberFormatError) as exc_info:
        Group(invalid_group_number)

    assert exc_info.value.args[0] == f'Invalid group number: {invalid_group_number!r}'


@pytest.mark.parametrize('group_number', _VALID_GROUP_NUMBERS)
def test_group_entity_equal(group_number: str):
    """Тест должен проверить равенство двух равных сущностей Group"""
    first_group = Group(group_number)
    second_group = Group(group_number)

    assert first_group == second_group


@pytest.mark.parametrize('group_number', _VALID_GROUP_NUMBERS)
def test_group_entity_equal_hash(group_number: str):
    """Тест должен проверить равенство хэша двух равных сущностей Group"""
    first_group = Group(group_number)
    second_group = Group(group_number)

    assert hash(first_group) == hash(second_group)


@pytest.mark.parametrize('group_item', _GROUP_ITEMS)
def test_group_entity_string_representation(group_item: Group):
    """Тест должен вернуть номер группы при str(group_item)"""

    assert str(group_item) == group_item.number
