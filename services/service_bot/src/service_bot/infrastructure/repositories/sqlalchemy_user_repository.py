import json
import logging
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
)
from service_bot.infrastructure.db.mappers import (
    user_domain_to_orm,
    user_orm_to_domain,
)

logger = logging.getLogger(__name__)


class SQLAlchemyUserRepository(UserRepository):
    """Репозиторий SQLAlchemyRepository [Реализация репозитория UserRepository]"""

    def __init__(self, session: 'AsyncSession'):
        self.session = session

    async def save(self, user_id: int) -> 'User':
        """Сохранение пользователя в базу данных"""
        user_orm = user_domain_to_orm(User(user_id=user_id))

        logger.info('Saving the user profile to the database')
        merged_orm = await self.session.merge(user_orm)
        logger.info('The user profile has been saved to the database')

        return_user = user_orm_to_domain(merged_orm)

        return return_user

    async def get_by_id(self, user_id: int) -> 'User':
        """Получение пользователя по user ID"""
        stmt = (select(UserORM).where(UserORM.user_id == user_id))

        logger.info('Retrieving a user profile from the database')
        user_orm: UserORM | None = await self.session.scalar(stmt)

        if user_orm is None:
            logger.warning('The user profile was not found in the database')
            raise UserNotFound(f'User with ID {user_id} not found')

        logger.info('The user profile is obtained from the database.')

        try:
            logger.info('Converting an ORM model into a domain entity')
            user_domain = user_orm_to_domain(user_orm)
            logger.info('The ORM model has been converted into a domain entity')

            return user_domain
        except UserMetadataMissingError as e:
            logger.warning('The user profile record in the database does not contain the required metadata %s',
                           ', '.join(e.missing_keys))
            await self._insert_default_metadata(user_orm, e.missing_keys)

            logger.info('Converting an ORM model into a domain entity')
            user_domain = user_orm_to_domain(user_orm)
            logger.info('The ORM model has been converted into a domain entity')

            return user_domain

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
            logger.info('Saving user metadata with the key %s to the database', key)
            await self.session.execute(stmt)
            logger.info('The user’s metadata is saved in the database')
        except (SQLAlchemyError, IntegrityError, TimeoutError):
            logger.exception('Error while executing the database query')
            user.metadata[key] = old_metadata_value
            raise

    async def subscribe_group(self, user: 'User', group: 'Group') -> None:
        """Подписка на кабинет"""
        stmt = (insert(GroupSubscribesORM).
                values(user_id=user.user_id, group_index=group.index).
                on_conflict_do_nothing().
                returning(GroupSubscribesORM.group_index))

        logger.info('Saving the record of the group subscription in the database')
        inserted = await self.session.scalar(stmt)

        if inserted is None:
            logger.warning('The database already contains a record of the subscription to the group')
            raise GroupAlreadyInsertedError(group.number)

        logger.info('The record of the subscription to the group has been saved in the database')

        user.group_subscribes = [*user.group_subscribes, group.index]

    async def subscribe_cabinet(self, user: 'User', cabinet: 'Cabinet') -> None:
        """Подписка на кабинет"""
        stmt = (insert(CabinetSubscribesORM).
                values(user_id=user.user_id, cabinet_index=cabinet.index).
                on_conflict_do_nothing().
                returning(CabinetSubscribesORM.cabinet_index))

        logger.info('Saving the record of the cabinet subscription in the database')
        inserted = await self.session.scalar(stmt)

        if inserted is None:
            logger.warning('The database already contains a record of the subscription to the cabinet')
            raise CabinetAlreadyInsertedError(f'User already subscribed at cabinet with index {cabinet.index!r}')

        logger.info('The record of the subscription to the cabinet has been saved in the database')

        user.cabinet_subscribes = [*user.cabinet_subscribes, cabinet.index]

    async def unsubscribe_group(self, user: 'User', group_index: str) -> None:
        """Отписка от группы"""
        logger.info('Deleting the group subscription record from the database')

        if group_index not in user.group_subscribes:
            logger.warning('There is no record of a subscription to the group in the database')
            raise GroupUnsubscribeNotFound()

        stmt = (delete(GroupSubscribesORM).
                where(GroupSubscribesORM.user_id == user.user_id,
                      GroupSubscribesORM.group_index == group_index))

        await self.session.execute(stmt)

        logger.info('The record of the group subscription has been deleted from the database')

        user.group_subscribes = [group_subscribed for group_subscribed in user.group_subscribes
                                 if group_subscribed != group_index]

    async def unsubscribe_cabinet(self, user: 'User', cabinet_index: str) -> None:
        """Отписка от кабинета"""
        logger.info('Deleting the cabinet subscription record from the database')

        if cabinet_index not in user.cabinet_subscribes:
            logger.warning('There is no record of a subscription to the cabinet in the database')
            raise CabinetUnsubscribeNotFound()

        stmt = (delete(CabinetSubscribesORM).
                where(CabinetSubscribesORM.user_id == user.user_id,
                      CabinetSubscribesORM.cabinet_index == cabinet_index))

        await self.session.execute(stmt)

        logger.info('The record of the cabinet subscription has been deleted from the database')

        user.cabinet_subscribes = [cabinet_subscribe for cabinet_subscribe in user.cabinet_subscribes
                                   if cabinet_subscribe != cabinet_index]

    async def _insert_default_metadata(self, user_orm: 'UserORM', keys: Iterable[str]) -> None:
        """Вставка стандартных метаданных"""
        logger.info('Saving missing user metadata to the database')
        keys_to_add = {key for key in keys if key in User._REQUIRED_METADATA}

        if not keys_to_add:
            logger.warning('The missing user profile metadata was not found')
            return

        for key in keys_to_add:
            user_orm.user_metadata.append(
                UserMetadataORM(key=key, value=json.dumps(User._DEFAULT_METADATA[key], ensure_ascii=False))
            )

        logger.info('The missing user metadata has been saved to the database')
