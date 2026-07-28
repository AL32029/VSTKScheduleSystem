from typing import Iterable

from schedule_db_models.models import CabinetORM
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from service_parser.application.ports import CabinetRepository
from service_parser.domain.entities import Cabinet
from service_parser.domain.exceptions.parser_exceptions import CabinetNotFound
from service_parser.infrastructure.db.mappers import cabinet_domain_to_orm, cabinet_orm_to_domain


class SQLAlchemyCabinetRepository(CabinetRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, cabinets: Iterable[Cabinet]) -> None:
        stmt = (
            insert(CabinetORM).
            values([
                {
                    k: v
                    for k, v in cabinet_domain_to_orm(cabinet).__dict__.items()
                    if k != '_sa_instance_state'
                }
                for cabinet in cabinets
            ]).
            on_conflict_do_nothing()
        )

        await self.session.execute(stmt)
        await self.session.commit()

    async def get_by_index(self, cabinet_index: str) -> Cabinet:
        cabinet_orm: CabinetORM | None = await self.session.get(CabinetORM, cabinet_index)

        if cabinet_orm is None:
            raise CabinetNotFound(f'Cabinet with index {str(cabinet_index)!r} not found')

        return cabinet_orm_to_domain(cabinet_orm)

    async def get_all(self) -> Iterable[Cabinet]:
        groups = await self.session.stream_scalars(select(CabinetORM))

        return [
            cabinet_orm_to_domain(group)
            async for group in groups
        ]
