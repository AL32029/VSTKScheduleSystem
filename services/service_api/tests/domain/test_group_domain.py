import pytest

from service_api.domain.entities import Group
from tests.test_contains import (
    _GROUP_ITEMS,
    _VALID_GROUP_NUMBERS,
)


# ====================== [ТЕСТЫ СУЩНОСТИ GROUP] ======================
@pytest.mark.parametrize(("index", "number"), _VALID_GROUP_NUMBERS)
def test_create_group_entity(index: str, number: str):
    """Тест должен корректно создать сущность Group"""
    group = Group(index, number)

    assert group.number == number
    assert group.index == index


@pytest.mark.parametrize(("index", "number"), _VALID_GROUP_NUMBERS)
def test_group_entity_equal(index: str, number: str):
    """Тест должен проверить равенство двух равных сущностей Group"""
    first_group = Group(index, number)
    second_group = Group(index, number)

    assert first_group == second_group


@pytest.mark.parametrize(("index", "number"), _VALID_GROUP_NUMBERS)
def test_group_entity_equal_hash(index: str, number: str):
    """Тест должен проверить равенство хэша двух равных сущностей Group"""
    first_group = Group(index, number)
    second_group = Group(index, number)

    assert hash(first_group) == hash(second_group)


@pytest.mark.parametrize("group_item", _GROUP_ITEMS)
def test_group_entity_string_representation(group_item: Group):
    """Тест должен вернуть номер группы при str(group_item)"""

    assert str(group_item) == group_item.number
