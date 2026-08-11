from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter

from service_api.application.services import GetAllCabinetsUseCase, GetCabinetUseCase
from service_api.infrastructure.mappers import (
    schedule_domain_to_schema,
    schedule_item_schema_to_response,
)
from service_api.infrastructure.pydantic_schemas import (
    ResponseSchema,
)

cabinet_router = APIRouter(prefix='/cabinets', tags=['Cabinet Items'])


@cabinet_router.get('/{cabinet_number}', response_model=ResponseSchema)
@inject
async def get_cabinet_by_number(cabinet_number: str, repo: FromDishka['GetCabinetUseCase']) -> 'ResponseSchema':
    schema = schedule_domain_to_schema(await repo.execute(cabinet_number))

    return schedule_item_schema_to_response(schema)


@cabinet_router.get('/', response_model=ResponseSchema)
@inject
async def get_all_cabinets(repo: FromDishka['GetAllCabinetsUseCase']) -> 'ResponseSchema':
    schemas = [schedule_domain_to_schema(cabinet) for cabinet in await repo.execute()]

    return schedule_item_schema_to_response(schemas)
