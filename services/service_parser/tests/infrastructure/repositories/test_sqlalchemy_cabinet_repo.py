from collections.abc import Iterable

import pytest
from patterns import ITEM_INDEX

from service_parser.domain.entities import Cabinet
from service_parser.domain.exceptions import CabinetNotFound

# ===================== [СУЩНОСТИ ДЛЯ ТЕСТОВ] =====================
_CABINET_NUMBERS = ['упм. 1, л. 6', 'сз3', '52к']
_CABINET_ITEMS = [Cabinet(cabinet)
                  for cabinet in _CABINET_NUMBERS]


# ===================== [ТЕСТЫ МЕТОДА SAVE] =====================
@pytest.mark.parametrize('cabinet', _CABINET_ITEMS)
async def test_save_cabinet(sqlalchemy_cabinet_repo, cabinet):
    """Тест должен корректно сохранить сущность Cabinet в базу данных"""
    await sqlalchemy_cabinet_repo.save([cabinet])

    cabinet_item = await sqlalchemy_cabinet_repo.get_by_index(cabinet.index)

    assert cabinet_item == cabinet


async def test_save_many_cabinets(sqlalchemy_cabinet_repo):
    """Тест должен корректно сохранить несколько сущностей Cabinet в базу данных"""
    await sqlalchemy_cabinet_repo.save(_CABINET_ITEMS)

    cabinets = await sqlalchemy_cabinet_repo.get_all()

    assert cabinets
    assert len(list(cabinets)) == len(_CABINET_ITEMS)


# ===================== [ТЕСТЫ МЕТОДА GET_BY_INDEX] =====================
@pytest.mark.parametrize("cabinet_number", _CABINET_NUMBERS)
async def test_get_by_index_error_not_found(sqlalchemy_cabinet_repo, cabinet_number):
    """Тест должен выдать ошибку GroupNotFound"""
    cabinet_index = ITEM_INDEX.sub('', cabinet_number)

    with pytest.raises(CabinetNotFound) as exc_info:
        await sqlalchemy_cabinet_repo.get_by_index(cabinet_index)

    assert exc_info.value.args[0] == f'Cabinet with index {cabinet_index!r} not found'


# ===================== [ТЕСТЫ МЕТОДА GET_ALL] =====================
async def test_get_all_empty_list(sqlalchemy_cabinet_repo):
    """Тест должен выдать пустой список"""
    cabinets = await sqlalchemy_cabinet_repo.get_all()

    assert isinstance(cabinets, Iterable)
    assert not cabinets
