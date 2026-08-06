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
)
from service_api.infrastructure.pydantic_schemas import (
    CabinetDayScheduleSchema,
    GroupDayScheduleSchema,
)

schedule_router = APIRouter(prefix='/schedule', tags=['Schedule Items'])


@schedule_router.get('/group', response_model=GroupDayScheduleSchema)
@inject
async def get_group_day_schedule(group_number: str, schedule_to: Literal['today', 'tomorrow'],
                                 use_case: FromDishka['GetGroupDayScheduleUseCase']) -> 'GroupDayScheduleSchema':
    day_schedule = await use_case.execute(group_number, schedule_to)

    return group_day_schedule_to_schema(day_schedule)


@schedule_router.get('/cabinet', response_model=CabinetDayScheduleSchema)
@inject
async def get_cabinet_day_schedule(cabinet_number: str, schedule_to: Literal['today', 'tomorrow'],
                                   use_case: FromDishka['GetCabinetDayScheduleUseCase']) -> 'CabinetDayScheduleSchema':
    day_schedule = await use_case.execute(cabinet_number, schedule_to)

    return cabinet_day_schedule_to_schema(day_schedule)
