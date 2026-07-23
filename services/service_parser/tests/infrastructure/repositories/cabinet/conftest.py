import pytest

from service_parser.domain.entities import Cabinet


@pytest.fixture
def cabinet_domain() -> Cabinet:
    return Cabinet('упм. 1, л. 6')


@pytest.fixture
async def cabinet_domain_saved(cabinet_repository, cabinet_domain):
    await cabinet_repository.save(cabinet_domain)

    return cabinet_domain
