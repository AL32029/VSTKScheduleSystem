import pytest

from service_parser.domain.entities import Cabinet
from service_parser.domain.exceptions.parser_exceptions import ScheduleCabinetNotFound


@pytest.mark.parametrize("cabinet_number", [
    '315', 'упм. 1, л. 6', '52к', 'сз3', 'экскурсия', 'тир, корп. 2'
])
async def test_create_cabinet_use_case(cabinet_repository, create_cabinet_use_case, cabinet_number):
    cabinet = await create_cabinet_use_case.execute(cabinet_number)

    assert cabinet is not None
    assert isinstance(cabinet, Cabinet)
    assert cabinet.number == cabinet_number
    assert cabinet.index is not None

    cabinet_db = await cabinet_repository.get_by_index(cabinet_index=cabinet.index)

    assert cabinet_db is not None
    assert cabinet_db == cabinet


@pytest.mark.parametrize("cabinet_number", [
    '315', 'упм. 1, л. 6', '52к', 'сз3', 'экскурсия', 'тир, корп. 2'
])
async def test_get_cabinet_by_index_use_case(create_cabinet_use_case, get_cabinet_by_index_use_case, cabinet_number):
    saved_cabinet = await create_cabinet_use_case.execute(cabinet_number)

    cabinet = await get_cabinet_by_index_use_case.execute(saved_cabinet)

    assert cabinet is not None
    assert cabinet.number == cabinet_number
    assert saved_cabinet == cabinet


@pytest.mark.parametrize("cabinet_number", [
    '315', 'упм. 1, л. 6', '52к', 'сз3', 'экскурсия', 'тир, корп. 2'
])
async def test_get_cabinet_by_index_use_case_not_found(get_cabinet_by_index_use_case, cabinet_number):
    with pytest.raises(ScheduleCabinetNotFound) as exc_info:
        await get_cabinet_by_index_use_case.execute(cabinet_number)

    assert exc_info.value.args[0] == f'Cabinet with index {str(Cabinet(cabinet_number).index)!r} not found'


@pytest.mark.parametrize("cabinet_numbers", [
    ['315', 'упм. 1, л. 6', '52к', 'сз3', 'экскурсия', 'тир, корп. 2']
])
async def test_get_all_cabinets_use_case(create_cabinet_use_case, get_all_cabinets_use_case, cabinet_numbers):
    for cabinet in cabinet_numbers:
        await create_cabinet_use_case.execute(cabinet)

    cabinets = sorted(await get_all_cabinets_use_case.execute(), key=lambda x: x.index)
    cabinet_numbers = sorted(cabinet_numbers, key=lambda x: Cabinet(x).index)

    assert all(isinstance(cabinet, Cabinet) for cabinet in cabinets)
    assert len(list(cabinets)) == len(cabinet_numbers)
    assert all(cabinet == Cabinet(cabinet_number) for cabinet, cabinet_number in zip(cabinets, cabinet_numbers))
