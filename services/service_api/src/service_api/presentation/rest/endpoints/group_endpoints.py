from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from pydantic import TypeAdapter

from service_api.application.services import GetAllGroupsUseCase, GetGroupUseCase
from service_api.infrastructure.pydantic_items import (
    ScheduleItemSchema,
    schedule_domain_to_schema,
)

all_groups_annotated = TypeAdapter(list['ScheduleItemSchema'])

group_router = APIRouter(prefix='/groups', tags=['Group Items'])


@group_router.get('/{group_number}', response_model=ScheduleItemSchema)
@inject
async def get_group_by_number(group_number: str, repo: 'FromDishka[GetGroupUseCase]') -> 'ScheduleItemSchema':
    group_item = await repo.execute(group_number)

    return schedule_domain_to_schema(group_item)


@group_router.get('/', response_model=list['ScheduleItemSchema'])
@inject
async def get_all_groups(repo: 'FromDishka[GetAllGroupsUseCase]') -> 'list[ScheduleItemSchema]':
    group_items = await repo.execute()

    return [schedule_domain_to_schema(group) for group in group_items]
