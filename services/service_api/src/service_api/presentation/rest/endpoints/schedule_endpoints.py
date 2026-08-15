from typing import Literal

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter

from service_api.application.services import (
    GetCabinetDayScheduleUseCase,
    GetGroupDayScheduleUseCase,
)
from service_api.infrastructure.mappers import (
    cabinet_day_schedule_to_schema,
    group_day_schedule_to_schema,
    schedule_item_schema_to_response,
)
from service_api.infrastructure.pydantic_schemas import (
    ResponseSchema,
)

schedule_router = APIRouter(prefix="/schedule", tags=["Schedule Items"])


@schedule_router.get("/group", response_model=ResponseSchema)
@inject
async def get_group_day_schedule(
    group_number: str,
    schedule_to: Literal["today", "tomorrow"],
    use_case: FromDishka["GetGroupDayScheduleUseCase"],
) -> "ResponseSchema":
    schema = group_day_schedule_to_schema(
        await use_case.execute(group_number, schedule_to)
    )

    return schedule_item_schema_to_response(schema)


@schedule_router.get("/cabinet", response_model=ResponseSchema)
@inject
async def get_cabinet_day_schedule(
    cabinet_number: str,
    schedule_to: Literal["today", "tomorrow"],
    use_case: FromDishka["GetCabinetDayScheduleUseCase"],
) -> "ResponseSchema":
    schema = cabinet_day_schedule_to_schema(
        await use_case.execute(cabinet_number, schedule_to)
    )

    return schedule_item_schema_to_response(schema)
