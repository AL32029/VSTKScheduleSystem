import pytest

from service_bot.domain.entities import Cabinet
from tests.test_contains import _CABINET_NUMBERS


# ====================== [ТЕСТЫ СУЩНОСТИ GROUP] ======================
@pytest.mark.parametrize('index, number', _CABINET_NUMBERS)
def test_cabinet_entity_eq_hash(index: str, number: str):
    """Тест должен проверить идентичность хэшей идентичных сущностей Cabinet"""
    first_item = Cabinet(index, number)
    second_item = Cabinet(index, number)

    assert hash(first_item) == hash(second_item)

@pytest.mark.parametrize('index, number', _CABINET_NUMBERS)
def test_cabinet_entity_eq(index: str, number: str):
    """Тест должен сравнить одинаковые сущности Cabinet"""
    first_item = Cabinet(index, number)
    second_item = Cabinet(index, number)

    assert first_item == second_item

@pytest.mark.parametrize('index, number', _CABINET_NUMBERS)
def test_cabinet_display_name(index: str, number: str):
    """Тест должен проверить вывод str(Cabinet)"""
    item = Cabinet(index, number)

    assert str(item) == item.number
