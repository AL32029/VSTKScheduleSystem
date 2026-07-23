import pytest

from service_parser.application.services.cabinet_use_case import CreateCabinetUseCase, GetCabinetByIndexUseCase, \
    GetAllCabinetsUseCase


@pytest.fixture
async def create_cabinet_use_case(cabinet_repository) -> CreateCabinetUseCase:
    return CreateCabinetUseCase(cabinet_repository)


@pytest.fixture
async def get_cabinet_by_index_use_case(cabinet_repository) -> GetCabinetByIndexUseCase:
    return GetCabinetByIndexUseCase(cabinet_repository)


@pytest.fixture
async def get_all_cabinets_use_case(cabinet_repository) -> GetAllCabinetsUseCase:
    return GetAllCabinetsUseCase(cabinet_repository)
