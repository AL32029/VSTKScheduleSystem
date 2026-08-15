import pytest

from service_api.domain.entities import Cabinet
from tests.test_contains import _CABINET_ITEMS, _VALID_CABINET_NUMBERS


# ====================== [ТЕСТЫ СУЩНОСТИ CABINET] ======================
@pytest.mark.parametrize("index, number", _VALID_CABINET_NUMBERS)
def test_create_cabinet_entity(index: str, number: str):
    """Тест должен корректно создать сущность Cabinet"""
    cabinet = Cabinet(index, number)

    assert cabinet.number == number
    assert cabinet.index == index


@pytest.mark.parametrize("index, number", _VALID_CABINET_NUMBERS)
def test_cabinet_entity_equal(index: str, number: str):
    """Тест должен проверить равенство двух равных сущностей Cabinet"""
    first_cabinet = Cabinet(index, number)
    second_cabinet = Cabinet(index, number)

    assert first_cabinet == second_cabinet


@pytest.mark.parametrize("index, number", _VALID_CABINET_NUMBERS)
def test_cabinet_entity_equal_hash(index: str, number: str):
    """Тест должен проверить равенство хэша двух равных сущностей Cabinet"""
    first_cabinet = Cabinet(index, number)
    second_cabinet = Cabinet(index, number)

    assert hash(first_cabinet) == hash(second_cabinet)


@pytest.mark.parametrize("cabinet_item", _CABINET_ITEMS)
def test_cabinet_entity_string_representation(cabinet_item: Cabinet):
    """Тест должен вернуть номер группы при str(cabinet_item)"""

    assert str(cabinet_item) == cabinet_item.number
