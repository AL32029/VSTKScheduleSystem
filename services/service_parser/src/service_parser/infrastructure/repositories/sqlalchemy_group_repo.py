import logging
from collections.abc import Iterable

from schedule_db_models import GroupORM
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from service_parser.application.ports import GroupRepository
from service_parser.domain.entities import Group
from service_parser.domain.exceptions import GroupNotFound
from service_parser.infrastructure.domain_mappers import (
    group_domain_to_orm,
    group_orm_to_domain,
)

logger = logging.getLogger(__name__)

class SQLAlchemyGroupRepository(GroupRepository):
    def __init__(self, session: 'AsyncSession'):
        self.session = session

    async def save(self, groups: Iterable['Group']) -> None:
        group_list = list(groups)
        logger.debug('Saving %d groups to database', len(group_list))
        stmt = (
            insert(GroupORM).
            values([
                {
                    k: v
                    for k, v in group_domain_to_orm(group).__dict__.items()
                    if k != '_sa_instance_state'
                }
                for group in group_list
            ]).
            on_conflict_do_nothing()
        )

        await self.session.execute(stmt)
        await self.session.commit()
        logger.debug('%d groups saved to database', len(group_list))

    async def delete(self, group: 'Group') -> None:
        logger.debug('Deleting group %s from database', group.number)
        group_orm = await self.session.get(GroupORM, group.index)

        if group_orm is None:
            logger.debug('Group %s not found in database, skipping deletion', group.number)
            raise GroupNotFound(f'Group with index {group.index!r} not found')

        await self.session.delete(group_orm)
        await self.session.commit()
        logger.debug('Group %s deleted from database', group.number)

    async def get_by_index(self, group_index: str) -> 'Group | None':
        logger.debug('Requesting group by index %s from database', group_index)
        group_orm: GroupORM | None = await self.session.get(GroupORM, group_index)

        if group_orm is None:
            logger.debug('Group with index %s not found in database', group_index)
            raise GroupNotFound(f'Group with index {group_index!r} not found')

        logger.debug('Group with index %s found in database', group_index)
        return group_orm_to_domain(group_orm)

    async def get_all(self) -> list['Group']:
        logger.debug('Requesting all groups from database')
        result = await self.session.stream_scalars(select(GroupORM))
        groups = [group_orm_to_domain(group) async for group in result]

        logger.debug('Retrieved %d groups from database', len(groups))
        return groups
