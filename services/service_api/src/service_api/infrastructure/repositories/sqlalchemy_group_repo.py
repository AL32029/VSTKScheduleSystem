from schedule_db_models import GroupORM
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from service_api.application.ports import GroupRepository
from service_api.domain.entities import Group
from service_api.domain.exceptions import GroupNotFound
from service_api.domain.shared.patterns import ITEM_INDEX
from service_api.infrastructure.mappers import group_orm_to_domain


class SQLAlchemyGroupRepository(GroupRepository):
    def __init__(self, session: 'AsyncSession'):
        self.session = session

    async def get_by_number(self, number: str) -> 'Group':
        group = await self.session.get(GroupORM, ITEM_INDEX.sub('', number.lower()))

        if group is None:
            raise GroupNotFound(number)

        return group_orm_to_domain(group)

    async def get_all(self) -> list['Group']:
        stmt = (
            select(GroupORM).
            order_by(GroupORM.index)
        )

        result = await self.session.stream_scalars(stmt)

        return [
            group_orm_to_domain(group)
            async for group in result
        ]
