import pytest

from service_parser.domain.entities import Cabinet
from service_parser.domain.shared.patterns import ITEM_INDEX

# ====================== [ВАЛИДНЫЕ ЗНАЧЕНИЯ] ======================
_VALID_CABINET_NUMBERS = ['упм. 1, л. 6', 'сз3', '52к']

# ====================== [СУЩНОСТИ] ======================
_CABINET_ITEMS = [Cabinet('упм. 1, л. 6'), Cabinet('сз3'), Cabinet('52к')]


# ====================== [ТЕСТЫ СУЩНОСТИ CABINET] ======================
@pytest.mark.parametrize('cabinet_number', _VALID_CABINET_NUMBERS)
def test_create_cabinet_entity(cabinet_number: str):
    """Тест должен корректно создать сущность Cabinet"""
    cabinet = Cabinet(cabinet_number)

    assert cabinet.number == cabinet_number
    assert cabinet.index == ITEM_INDEX.sub('', cabinet_number.lower())


@pytest.mark.parametrize('cabinet_number', _VALID_CABINET_NUMBERS)
def test_cabinet_entity_equal(cabinet_number: str):
    """Тест должен проверить равенство двух равных сущностей Cabinet"""
    first_cabinet = Cabinet(cabinet_number)
    second_cabinet = Cabinet(cabinet_number)

    assert first_cabinet == second_cabinet


@pytest.mark.parametrize('cabinet_number', _VALID_CABINET_NUMBERS)
def test_cabinet_entity_equal_hash(cabinet_number: str):
    """Тест должен проверить равенство хэша двух равных сущностей Cabinet"""
    first_cabinet = Cabinet(cabinet_number)
    second_cabinet = Cabinet(cabinet_number)

    assert hash(first_cabinet) == hash(second_cabinet)


@pytest.mark.parametrize('cabinet_item', _CABINET_ITEMS)
def test_cabinet_entity_string_representation(cabinet_item: Cabinet):
    """Тест должен вернуть номер группы при str(cabinet_item)"""

    assert str(cabinet_item) == cabinet_item.number
