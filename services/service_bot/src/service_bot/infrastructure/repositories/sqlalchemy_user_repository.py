import json
from collections.abc import Iterable
from typing import Any

from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from service_bot.application.ports import UserRepository
from service_bot.domain.entities import Cabinet, Group, User
from service_bot.domain.exceptions import (
    CabinetAlreadyInsertedError,
    CabinetUnsubscribeNotFound,
    GroupAlreadyInsertedError,
    GroupUnsubscribeNotFound,
    UserMetadataMissingError,
    UserNotFound,
)
from service_bot.infrastructure.db import (
    CabinetSubscribesORM,
    GroupSubscribesORM,
    UserMetadataORM,
    UserORM,
    user_domain_to_orm,
    user_orm_to_domain,
)


class SQLAlchemyUserRepository(UserRepository):
    """Репозиторий SQLAlchemyRepository [Реализация репозитория UserRepository]"""

    def __init__(self, session: 'AsyncSession'):
        self.session = session

    async def save(self, user_id: int) -> 'User':
        """Сохранение пользователя в базу данных"""
        user_orm = user_domain_to_orm(User(user_id=user_id))

        merged_orm = await self.session.merge(user_orm)

        return_user = user_orm_to_domain(merged_orm)

        return return_user

    async def get_by_id(self, user_id: int) -> 'User':
        """Получение пользователя по user ID"""
        stmt = (select(UserORM).where(UserORM.user_id == user_id))

        user_orm: UserORM | None = await self.session.scalar(stmt)

        if user_orm is None:
            raise UserNotFound(f'User with ID {user_id} not found')

        try:
            return user_orm_to_domain(user_orm)
        except UserMetadataMissingError as e:
            await self._insert_default_metadata(user_orm, e.missing_keys)

            return user_orm_to_domain(user_orm)

    async def update_metadata(self, user: 'User', key: str, value: Any) -> None:
        """Обновление метаданных пользователя"""
        old_metadata_value = user.metadata.get(key)

        user.update_metadata(key, value)

        stmt = (
            update(UserMetadataORM).
            where(UserMetadataORM.user_id == user.user_id, UserMetadataORM.key == key).
            values(value=json.dumps(value, ensure_ascii=False))
        )

        try:
            await self.session.execute(stmt)
        except (SQLAlchemyError, IntegrityError, TimeoutError):
            user.metadata[key] = old_metadata_value
            raise

    async def subscribe_group(self, user: 'User', group: 'Group') -> None:
        """Подписка на кабинет"""
        stmt = (insert(GroupSubscribesORM).
                values(user_id=user.user_id, group_index=group.index).
                on_conflict_do_nothing().
                returning(GroupSubscribesORM.group_index))

        inserted = await self.session.scalar(stmt)

        if inserted is None:
            raise GroupAlreadyInsertedError(group.number)

        user.group_subscribes = [*user.group_subscribes, group.index]

    async def subscribe_cabinet(self, user: 'User', cabinet: 'Cabinet') -> None:
        """Подписка на кабинет"""
        stmt = (insert(CabinetSubscribesORM).
                values(user_id=user.user_id, cabinet_index=cabinet.index).
                on_conflict_do_nothing().
                returning(CabinetSubscribesORM.cabinet_index))

        inserted = await self.session.scalar(stmt)

        if inserted is None:
            raise CabinetAlreadyInsertedError(f'User already subscribed at cabinet with index {cabinet.index!r}')

        user.cabinet_subscribes = [*user.cabinet_subscribes, cabinet.index]

    async def unsubscribe_group(self, user: 'User', group_index: str) -> None:
        """Отписка от группы"""
        if group_index not in user.group_subscribes:
            raise GroupUnsubscribeNotFound()

        stmt = (delete(GroupSubscribesORM).
                where(GroupSubscribesORM.user_id == user.user_id,
                      GroupSubscribesORM.group_index == group_index))

        await self.session.execute(stmt)

        user.group_subscribes = [group_subscribed for group_subscribed in user.group_subscribes
                                 if group_subscribed != group_index]

    async def unsubscribe_cabinet(self, user: 'User', cabinet_index: str) -> None:
        """Отписка от кабинета"""
        if cabinet_index not in user.cabinet_subscribes:
            raise CabinetUnsubscribeNotFound()

        stmt = (delete(CabinetSubscribesORM).
                where(CabinetSubscribesORM.user_id == user.user_id,
                      CabinetSubscribesORM.cabinet_index == cabinet_index))

        await self.session.execute(stmt)

        user.cabinet_subscribes = [cabinet_subscribe for cabinet_subscribe in user.cabinet_subscribes
                                   if cabinet_subscribe != cabinet_index]

    async def _insert_default_metadata(self, user_orm: 'UserORM', keys: Iterable[str]) -> None:
        """Вставка стандартных метаданных"""
        keys_to_add = {key for key in keys if key in User._REQUIRED_METADATA}

        if not keys_to_add:
            return

        for key in keys_to_add:
            user_orm.user_metadata.append(
                UserMetadataORM(key=key, value=json.dumps(User._DEFAULT_METADATA[key], ensure_ascii=False))
            )
