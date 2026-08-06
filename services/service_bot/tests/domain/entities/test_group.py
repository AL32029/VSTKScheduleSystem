import pytest

from service_bot.domain.entities import Group
from tests.test_contains import _GROUP_NUMBERS


# ====================== [ТЕСТЫ СУЩНОСТИ GROUP] ======================
@pytest.mark.parametrize('index, number', _GROUP_NUMBERS)
def test_group_entity_eq_hash(index: str, number: str):
    """Тест должен проверить идентичность хэшей идентичных сущностей Group"""
    first_item = Group(index, number)
    second_item = Group(index, number)

    assert hash(first_item) == hash(second_item)

@pytest.mark.parametrize('index, number', _GROUP_NUMBERS)
def test_group_entity_eq(index: str, number: str):
    """Тест должен сравнить одинаковые сущности Group"""
    first_item = Group(index, number)
    second_item = Group(index, number)

    assert first_item == second_item

@pytest.mark.parametrize('index, number', _GROUP_NUMBERS)
def test_group_display_name(index: str, number: str):
    """Тест должен проверить вывод str(Group)"""
    item = Group(index, number)

    assert str(item) == item.number
