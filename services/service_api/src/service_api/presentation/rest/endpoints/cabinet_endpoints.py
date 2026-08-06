from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter

from service_api.application.services import GetAllCabinetsUseCase, GetCabinetUseCase
from service_api.infrastructure.mappers import schedule_domain_to_schema
from service_api.infrastructure.pydantic_schemas import ScheduleItemSchema

cabinet_router = APIRouter(prefix='/cabinets', tags=['Cabinet Items'])


@cabinet_router.get('/{cabinet_number}', response_model=ScheduleItemSchema)
@inject
async def get_cabinet_by_number(cabinet_number: str, repo: FromDishka['GetCabinetUseCase']) -> 'ScheduleItemSchema':
    cabinet = await repo.execute(cabinet_number)

    return schedule_domain_to_schema(cabinet)


@cabinet_router.get('/', response_model=list[ScheduleItemSchema])
@inject
async def get_all_cabinets(repo: FromDishka['GetAllCabinetsUseCase']) -> list['ScheduleItemSchema']:
    cabinet_items = await repo.execute()

    return [schedule_domain_to_schema(cabinet) for cabinet in cabinet_items]
