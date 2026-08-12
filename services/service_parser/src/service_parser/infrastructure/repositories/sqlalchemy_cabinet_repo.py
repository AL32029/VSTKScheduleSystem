import logging
from collections.abc import Iterable

from schedule_db_models import CabinetORM
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from service_parser.application.ports import CabinetRepository
from service_parser.domain.entities import Cabinet
from service_parser.domain.exceptions import CabinetNotFound
from service_parser.infrastructure.domain_mappers import (
    cabinet_domain_to_orm,
    cabinet_orm_to_domain,
)

logger = logging.getLogger(__name__)


class SQLAlchemyCabinetRepository(CabinetRepository):
    def __init__(self, session: 'AsyncSession'):
        self.session = session

    async def save(self, cabinets: Iterable['Cabinet']) -> None:
        cabinet_list = list(cabinets)
        logger.debug('Saving %d cabinets to database', len(cabinet_list))
        stmt = (
            insert(CabinetORM).
            values([
                {
                    k: v
                    for k, v in cabinet_domain_to_orm(cabinet).__dict__.items()
                    if k != '_sa_instance_state'
                }
                for cabinet in cabinet_list
            ]).
            on_conflict_do_nothing()
        )

        await self.session.execute(stmt)
        await self.session.commit()
        logger.debug('%d cabinets saved to database', len(cabinet_list))

    async def get_by_index(self, cabinet_index: str) -> 'Cabinet':
        logger.debug('Requesting cabinet by index %s from database', cabinet_index)
        cabinet_orm: CabinetORM | None = await self.session.get(CabinetORM, cabinet_index)

        if cabinet_orm is None:
            logger.debug('Cabinet with index %s not found in database', cabinet_index)
            raise CabinetNotFound(f'Cabinet with index {str(cabinet_index)!r} not found')

        logger.debug('Cabinet with index %s found in database', cabinet_index)
        return cabinet_orm_to_domain(cabinet_orm)

    async def get_all(self) -> list['Cabinet']:
        logger.debug('Requesting all cabinets from database')
        result = await self.session.stream_scalars(select(CabinetORM))
        cabinets = [cabinet_orm_to_domain(cabinet) async for cabinet in result]

        logger.debug('Retrieved %d cabinets from database', len(cabinets))
        return cabinets
