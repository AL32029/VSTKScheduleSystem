from typing import Iterable

from schedule_db_models.models import GroupORM
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from service_parser.application.ports import GroupRepository
from service_parser.domain.entities import Group
from service_parser.domain.exceptions.parser_exceptions import GroupNotFound
from service_parser.infrastructure.db.mappers import group_domain_to_orm, group_orm_to_domain


class SQLAlchemyGroupRepository(GroupRepository):
    def __init__(self, session: 'AsyncSession'):
        self.session = session

    async def save(self, groups: Iterable['Group']) -> None:
        stmt = (
            insert(GroupORM).
            values([
                {
                    k: v
                    for k, v in group_domain_to_orm(group).__dict__.items()
                    if k != '_sa_instance_state'
                }
                for group in groups
            ]).
            on_conflict_do_nothing()
        )

        await self.session.execute(stmt)
        await self.session.commit()

    async def delete(self, group: 'Group') -> None:
        group_orm = await self.session.get(GroupORM, group.index)

        await self.session.delete(group_orm)
        await self.session.commit()

    async def get_by_index(self, group_index: str) -> 'Group | None':
        group_orm: 'GroupORM | None' = await self.session.get(GroupORM, group_index)

        if group_orm is None:
            raise GroupNotFound(f'Group with index {group_index!r} not found')

        return group_orm_to_domain(group_orm)

    async def get_all(self) -> list['Group']:
        groups = await self.session.stream_scalars(select(GroupORM))

        return [group_orm_to_domain(group)
                async for group in groups]
