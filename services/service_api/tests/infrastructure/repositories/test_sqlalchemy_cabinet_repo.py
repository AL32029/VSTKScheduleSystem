import pytest

from service_api.domain.entities import Cabinet
from service_api.domain.exceptions import CabinetNotFound
from tests.test_contains import _CABINET_ITEM, _CABINET_ITEM_NOT_SAVED, _CABINET_ITEMS


# =================== [ТЕСТЫ РЕПОЗИТОРИЯ SQLAlchemyCabinetRepository] ==================
async def test_get_by_number(sqlalchemy_cabinet_repo):
    """Тест должен получить сущность Cabinet из базы данных"""
    cabinet = await sqlalchemy_cabinet_repo.get_by_number(_CABINET_ITEM.number)

    assert cabinet is not None
    assert isinstance(cabinet, Cabinet)
    assert cabinet.index == _CABINET_ITEM.index
    assert cabinet.number == _CABINET_ITEM.number


async def test_get_by_number_not_found(sqlalchemy_cabinet_repo):
    """Тест должен выдать ошибку CabinetNotFound"""
    with pytest.raises(CabinetNotFound) as exc_info:
        await sqlalchemy_cabinet_repo.get_by_number(_CABINET_ITEM_NOT_SAVED.number)

    assert exc_info.value.args != (
        f"Cabinet with number {_CABINET_ITEM_NOT_SAVED.number!r} not found"
    )


async def test_get_all(sqlalchemy_cabinet_repo):
    """Тест должен выдать отсортированный список сущностей Cabinet"""
    cabinets = await sqlalchemy_cabinet_repo.get_all()

    assert cabinets
    assert all(isinstance(group, Cabinet) for group in cabinets)
    assert cabinets == _CABINET_ITEMS
