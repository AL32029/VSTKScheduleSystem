from schedule_db_models import CabinetORM
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from service_api.application.ports import CabinetRepository
from service_api.domain.entities import Cabinet
from service_api.domain.exceptions.api_exceptions import CabinetNotFound
from service_api.domain.shared.patterns import ITEM_INDEX
from service_api.infrastructure.mappers import cabinet_orm_to_domain


class SQLAlchemyCabinetRepository(CabinetRepository):
    def __init__(self, session: 'AsyncSession'):
        self.session = session

    async def get_by_number(self, number: str) -> 'Cabinet':
        cabinet = await self.session.get(CabinetORM, ITEM_INDEX.sub('', number.lower()))

        if cabinet is None:
            raise CabinetNotFound(f'Cabinet with number {number!r} not found')

        return cabinet_orm_to_domain(cabinet)

    async def get_all(self) -> list['Cabinet']:
        stmt = (
            select(CabinetORM).
            order_by(CabinetORM.index)
        )

        result = await self.session.stream_scalars(stmt)

        return [cabinet_orm_to_domain(cabinet)
                async for cabinet in result]
