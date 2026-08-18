import logging
from collections.abc import Iterable

from schedule_db_models import GroupORM
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from service_parser.application.ports import GroupRepository
from service_parser.domain.entities import Group
from service_parser.domain.exceptions import GroupNotFoundError
from service_parser.infrastructure.domain_mappers import (
    group_domain_to_orm,
    group_orm_to_domain,
)

logger = logging.getLogger(__name__)


class SQLAlchemyGroupRepository(GroupRepository):
    def __init__(self, session: "AsyncSession"):
        self.session = session

    async def save(self, groups: Iterable["Group"]) -> None:
        group_list = list(groups)
        logger.debug("Saving %d groups to database", len(group_list))
        stmt = (
            update(GroupORM)
            .values(is_active=True)
            .where(GroupORM.index.in_(group.index for group in groups))
        )

        await self.session.execute(stmt)

        stmt = (
            insert(GroupORM)
            .values(
                [
                    {
                        k: v
                        for k, v in group_domain_to_orm(group).__dict__.items()
                        if k != "_sa_instance_state"
                    }
                    for group in group_list
                ]
            )
            .on_conflict_do_nothing()
        )

        await self.session.execute(stmt)
        await self.session.commit()
        logger.debug("%d groups saved to database", len(group_list))

    async def deactivate(self, groups: Iterable["Group"]) -> None:
        logger.debug("Deactivating %s groups from database", len(list(groups)))
        stmt = (
            update(GroupORM)
            .values(is_active=False)
            .where(GroupORM.index.in_(group.index for group in groups))
        )
        await self.session.execute(stmt)
        await self.session.commit()
        logger.debug("%s groups deactivated from database", len(list(groups)))

    async def get_by_index(self, group_index: str) -> "Group | None":
        logger.debug("Requesting group by index %s from database", group_index)
        group_orm: GroupORM | None = await self.session.get(GroupORM, group_index)

        if group_orm is None or not group_orm.is_active:
            logger.debug("Group with index %s not found in database", group_index)
            raise GroupNotFoundError(f"Group with index {group_index!r} not found")

        logger.debug("Group with index %s found in database", group_index)
        return group_orm_to_domain(group_orm)

    async def get_many(self, groups: Iterable["Group"]) -> list["Group"]:
        logger.debug("Requesting %s groups from database", len(list(groups)))
        stmt = (
            select(GroupORM)
            .where(
                GroupORM.index.in_(group.index for group in groups),
                GroupORM.is_active.is_(True),
            )
            .order_by(GroupORM.index)
        )
        groups_db = {
            group_orm_to_domain(group)
            async for group in await self.session.stream_scalars(stmt)
        }
        logger.debug("%s groups was found in database", len(list(groups_db)))
        return list(groups_db)

    async def get_all(self) -> list["Group"]:
        logger.debug("Requesting all groups from database")
        result = await self.session.stream_scalars(
            select(GroupORM).where(GroupORM.is_active.is_(True))
        )
        groups = [group_orm_to_domain(group) async for group in result]

        logger.debug("Retrieved %d groups from database", len(groups))
        return groups
