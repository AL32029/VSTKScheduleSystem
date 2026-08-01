import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture(scope='session')
def test_app(test_container):
    from service_api.main import create_app
    return create_app(test_container)


@pytest.fixture(scope="function")
async def client(test_app):
    async with AsyncClient(
            transport=ASGITransport(app=test_app),
            base_url="http://test"
    ) as client:
        yield client
