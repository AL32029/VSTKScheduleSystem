from collections.abc import Iterable
from typing import cast

from service_api.domain.entities import Cabinet
from service_api.infrastructure.pydantic_schemas import ScheduleItemSchema
from tests.test_contains import _CABINET_ITEM, _CABINET_ITEMS


# ====================== [ТЕСТЫ ЭНДПОИНТОВ КАБИНЕТОВ] ======================
async def test_get_cabinet_by_number_endpoint(client):
    """Тест должен выполнить HTTP запрос и получить JSON кабинетов"""
    resp = await client.get(f"/cabinets/{_CABINET_ITEM!s}")

    assert resp.status_code == 200

    response_data: dict = resp.json()

    print(resp.text, response_data)

    cabinet: Cabinet = cast(
        "Cabinet",
        ScheduleItemSchema.model_validate(response_data.get("data")).to_domain(
            "cabinet"
        ),
    )

    assert cabinet == _CABINET_ITEM


async def test_get_all_cabinets_endpoint(client):
    """Тест должен выполнить HTTP запрос и получить JSON всех кабинетов"""
    resp = await client.get("/cabinets/")

    assert resp.status_code == 200

    response_data: dict = resp.json()

    print(resp.text, response_data)

    schemas_list: list[dict] = cast(list[dict], response_data.get("data"))

    cabinets: Iterable[Cabinet] = [
        cast("Cabinet", ScheduleItemSchema.model_validate(cabinet).to_domain("cabinet"))
        for cabinet in schemas_list
    ]

    assert len(list(cabinets)) == len(_CABINET_ITEMS)
