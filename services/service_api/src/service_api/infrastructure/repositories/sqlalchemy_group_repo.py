import logging

from patterns import ITEM_INDEX
from schedule_db_models import GroupORM
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from service_api.application.ports import GroupRepository
from service_api.domain.entities import Group
from service_api.domain.exceptions import GroupNotFoundError
from service_api.infrastructure.mappers import group_orm_to_domain

logger = logging.getLogger(__name__)


class SQLAlchemyGroupRepository(GroupRepository):
    def __init__(self, session: "AsyncSession"):
        self.session = session

    async def get_by_number(self, number: str) -> "Group":
        logger.debug("Requesting group by number %s from database", number)
        group = await self.session.get(GroupORM, ITEM_INDEX.sub("", number.lower()))

        if group is None:
            logger.debug("Group %s not found in database", number)
            raise GroupNotFoundError(number)

        logger.debug("Group %s found in database", number)
        return group_orm_to_domain(group)

    async def get_all(self) -> list["Group"]:
        logger.debug("Requesting all groups from database")
        stmt = select(GroupORM).order_by(GroupORM.index)

        result = await self.session.stream_scalars(stmt)
        groups = [group_orm_to_domain(group) async for group in result]

        logger.debug("Retrieved %d groups from database", len(groups))
        return groups
