import logging

from patterns import ITEM_INDEX
from schedule_db_models import CabinetORM
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from service_api.application.ports import CabinetRepository
from service_api.domain.entities import Cabinet
from service_api.domain.exceptions import CabinetNotFoundError
from service_api.infrastructure.mappers import cabinet_orm_to_domain

logger = logging.getLogger(__name__)


class SQLAlchemyCabinetRepository(CabinetRepository):
    def __init__(self, session: "AsyncSession"):
        self.session = session

    async def get_by_number(self, number: str) -> "Cabinet":
        logger.debug("Requesting cabinet by number %s from database", number)
        cabinet = await self.session.get(CabinetORM, ITEM_INDEX.sub("", number.lower()))

        if cabinet is None:
            logger.debug("Cabinet %s not found in database", number)
            raise CabinetNotFoundError(number)

        logger.debug("Cabinet %s found in database", number)
        return cabinet_orm_to_domain(cabinet)

    async def get_all(self) -> list["Cabinet"]:
        logger.debug("Requesting all cabinets from database")
        stmt = select(CabinetORM).order_by(CabinetORM.index)

        result = await self.session.stream_scalars(stmt)
        cabinets = [cabinet_orm_to_domain(cabinet) async for cabinet in result]

        logger.debug("Retrieved %d cabinets from database", len(cabinets))
        return cabinets
