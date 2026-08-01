from typing import Literal

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, HTTPException

from service_api.domain.entities.get_cabinet_day_schedule import (
    GetCabinetDayScheduleUseCase,
)
from service_api.domain.entities.get_group_day_schedule import (
    GetGroupDayScheduleUseCase,
)
from service_api.domain.exceptions import (
    CabinetDayScheduleNotFound,
    CabinetNotFound,
    GroupDayScheduleNotFound,
    GroupNotFound,
    GroupNumberFormatError,
    ScheduleDateNotFound,
)
from service_api.presentation.rest.mappers import (
    cabinet_day_schedule_to_response,
    group_day_schedule_to_response,
)
from service_api.presentation.rest.schemas import (
    CabinetDayScheduleResponse,
    GroupDayScheduleResponse,
)

schedule_router = APIRouter(prefix='/schedule', tags=['Schedule Items'])

@schedule_router.get('/group', response_model=GroupDayScheduleResponse)
@inject
async def get_group_day_schedule(group_number: str, schedule_to: Literal['today', 'tomorrow'],
                                 use_case: FromDishka[GetGroupDayScheduleUseCase]) -> GroupDayScheduleResponse:
    try:
        day_schedule = await use_case.execute(group_number, schedule_to)
    except GroupNumberFormatError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except (GroupNotFound, ScheduleDateNotFound) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except GroupDayScheduleNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

    return group_day_schedule_to_response(day_schedule)


@schedule_router.get('/cabinet', response_model=CabinetDayScheduleResponse)
@inject
async def get_cabinet_day_schedule(cabinet_number: str, schedule_to: Literal['today', 'tomorrow'],
                                   use_case: FromDishka[GetCabinetDayScheduleUseCase]) -> CabinetDayScheduleResponse:
    try:
        day_schedule = await use_case.execute(cabinet_number, schedule_to)
    except (CabinetNotFound, ScheduleDateNotFound) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CabinetDayScheduleNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

    return cabinet_day_schedule_to_response(day_schedule)
