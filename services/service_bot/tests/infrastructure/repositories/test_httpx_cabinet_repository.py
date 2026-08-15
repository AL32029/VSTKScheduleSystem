from dataclasses import asdict

import pytest

from service_bot.domain.entities import Cabinet
from service_bot.domain.exceptions import CabinetNotFound
from tests.test_contains import _CABINET_ITEMS


@pytest.mark.parametrize("cabinet", _CABINET_ITEMS)
async def test_get_by_number(httpx_mock, client, httpx_cabinet_repository, cabinet):
    httpx_mock.add_response(
        method="GET",
        url=f"{client.base_url}/cabinets/{cabinet.number}",
        json={"success": True, "data": asdict(cabinet)},
    )

    cabinet_item = await httpx_cabinet_repository.get_by_number(cabinet.number)

    assert isinstance(cabinet_item, Cabinet)
    assert cabinet_item == cabinet


@pytest.mark.parametrize("cabinet", _CABINET_ITEMS)
async def test_get_by_number_not_found(
    httpx_mock, client, httpx_cabinet_repository, cabinet
):
    cabinet_number = str(cabinet)

    httpx_mock.add_response(
        method="GET",
        url=f"{client.base_url}/cabinets/{cabinet_number}",
        status_code=404,
        json={
            "success": False,
            "error": {
                "code": "CABINET_NOT_FOUND",
                "detail": f"Cabinet with number {cabinet_number!r} not found",
                "extra": {"input_number": cabinet_number},
            },
        },
    )

    with pytest.raises(CabinetNotFound) as exc_info:
        await httpx_cabinet_repository.get_by_number(cabinet_number)

    assert exc_info.value.args[0] == f"Кабинет {cabinet_number} не найден"


async def test_get_all(httpx_mock, client, httpx_cabinet_repository):
    httpx_mock.add_response(
        method="GET",
        url=f"{client.base_url}/cabinets/",
        json={
            "success": True,
            "data": [
                asdict(group) for group in sorted(_CABINET_ITEMS, key=lambda x: x.index)
            ],
        },
    )

    cabinet_items = await httpx_cabinet_repository.get_all()

    assert cabinet_items
    assert isinstance(cabinet_items, list)
    assert len(cabinet_items) == len(_CABINET_ITEMS)
    assert all(
        isinstance(cabinet, Cabinet)
        for cabinet in sorted(cabinet_items, key=lambda x: x.index)
    )
