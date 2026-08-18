from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Path

from service_api.application.services import GetAllGroupsUseCase, GetGroupUseCase
from service_api.infrastructure.mappers import (
    schedule_domain_to_schema,
    schedule_item_schema_to_response,
)
from service_api.infrastructure.pydantic_schemas import (
    ResponseSchema,
)

group_router = APIRouter(prefix="/groups", tags=["Group Items"])


@group_router.get("/{group_number}", response_model=ResponseSchema)
@inject
async def get_group_by_number(
    repo: FromDishka["GetGroupUseCase"],
    group_number: str = Path(min_length=1, max_length=32),
) -> "ResponseSchema":
    schema = schedule_domain_to_schema(await repo.execute(group_number))

    return schedule_item_schema_to_response(schema)


@group_router.get("/", response_model=ResponseSchema)
@inject
async def get_all_groups(repo: FromDishka["GetAllGroupsUseCase"]) -> "ResponseSchema":
    schemas = [schedule_domain_to_schema(group) for group in await repo.execute()]

    return schedule_item_schema_to_response(schemas)
