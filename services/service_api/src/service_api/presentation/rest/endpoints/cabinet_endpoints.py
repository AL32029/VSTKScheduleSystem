from dishka import FromDishka
from fastapi import HTTPException
from pydantic import TypeAdapter

from service_api.application.services import GetAllCabinetsUseCase, GetCabinetUseCase
from service_api.domain.exceptions import GroupNotFound, GroupNumberFormatError
from service_api.presentation.rest.mappers import schedule_domain_to_response
from service_api.presentation.rest.routers import cabinet_router
from service_api.presentation.rest.schemas import ScheduleItemResponse

all_groups_annotated = TypeAdapter(list[ScheduleItemResponse])


@cabinet_router.get('{cabinet_number}/', response_model=ScheduleItemResponse)
async def get_group_by_number(cabinet_number: str, repo: FromDishka[GetCabinetUseCase]) -> ScheduleItemResponse:
    try:
        cabinet = await repo.execute(cabinet_number)
    except GroupNumberFormatError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except GroupNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

    return schedule_domain_to_response(cabinet)


@cabinet_router.get('', response_model=list[ScheduleItemResponse])
async def get_all_groups(repo: FromDishka[GetAllCabinetsUseCase]) -> list[ScheduleItemResponse]:
    group_items = await repo.execute()

    return [schedule_domain_to_response(group) for group in group_items]