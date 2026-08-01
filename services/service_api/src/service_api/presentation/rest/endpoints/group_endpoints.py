from dishka import FromDishka
from fastapi import HTTPException
from pydantic import TypeAdapter

from service_api.application.services import GetAllGroupsUseCase, GetGroupUseCase
from service_api.domain.exceptions import GroupNotFound, GroupNumberFormatError
from service_api.presentation.rest.mappers import schedule_domain_to_response
from service_api.presentation.rest.routers import group_router
from service_api.presentation.rest.schemas import ScheduleItemResponse

all_groups_annotated = TypeAdapter(list[ScheduleItemResponse])


@group_router.get('{group_number}/', response_model=ScheduleItemResponse)
async def get_group_by_number(group_number: str, repo: FromDishka[GetGroupUseCase]) -> ScheduleItemResponse:
    try:
        group_item = await repo.execute(group_number)
    except GroupNumberFormatError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except GroupNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

    return schedule_domain_to_response(group_item)


@group_router.get('', response_model=list[ScheduleItemResponse])
async def get_all_groups(repo: FromDishka[GetAllGroupsUseCase]) -> list[ScheduleItemResponse]:
    group_items = await repo.execute()

    return [schedule_domain_to_response(group) for group in group_items]
