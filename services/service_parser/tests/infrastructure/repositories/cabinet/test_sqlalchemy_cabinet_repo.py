import pytest

from service_parser.domain.entities import Cabinet
from service_parser.domain.exceptions.parser_exceptions import ScheduleCabinetNotFound


async def test_cabinet_saving(cabinet_repository, cabinet_domain):
    await cabinet_repository.save(cabinet_domain)

    cabinet_db = await cabinet_repository.get_by_index(cabinet_domain.index)

    assert cabinet_db is not None
    assert isinstance(cabinet_db, Cabinet)
    assert cabinet_domain == cabinet_db


async def test_cabinet_get_by_index(cabinet_repository, cabinet_domain_saved):
    cabinet = await cabinet_repository.get_by_index(cabinet_domain_saved.index)

    assert cabinet is not None
    assert cabinet == cabinet_domain_saved


async def test_cabinet_get_by_index_not_found(cabinet_repository, cabinet_domain):
    with pytest.raises(ScheduleCabinetNotFound) as exc_info:
        await cabinet_repository.get_by_index(cabinet_domain.index)

    assert exc_info.value.args[0] == f'Cabinet with index {str(cabinet_domain.index)!r} not found'


async def test_cabinet_get_all(cabinet_repository, cabinet_domain_saved):
    cabinets = await cabinet_repository.get_all()

    assert cabinets is not None
    assert len(cabinets) == 1
    assert cabinets[0] == cabinet_domain_saved
