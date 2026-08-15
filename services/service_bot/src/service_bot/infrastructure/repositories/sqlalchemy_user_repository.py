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
    CabinetUnsubscribeNotFoundError,
    GroupAlreadyInsertedError,
    GroupUnsubscribeNotFoundError,
    UserMetadataMissingError,
    UserNotFoundError,
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

    def __init__(self, session: "AsyncSession"):
        self.session = session

    async def save(self, user_id: int) -> "User":
        """Сохранение пользователя в базу данных"""
        logger.debug("Saving user %d to database", user_id)
        user_orm = user_domain_to_orm(User(user_id=user_id))
        merged_orm = await self.session.merge(user_orm)
        logger.info("User %d saved to database", user_id)
        return user_orm_to_domain(merged_orm)

    async def get_by_id(self, user_id: int) -> "User":
        """Получение пользователя по user ID"""
        logger.debug("Retrieving user %d from database", user_id)
        stmt = select(UserORM).where(UserORM.user_id == user_id)
        user_orm: UserORM | None = await self.session.scalar(stmt)

        if user_orm is None:
            logger.warning("User %d not found in database", user_id)
            raise UserNotFoundError(f"User with ID {user_id} not found")

        try:
            user_domain = user_orm_to_domain(user_orm)
            logger.info("User %d retrieved from database", user_id)
            return user_domain
        except UserMetadataMissingError as e:
            logger.warning(
                "User %d metadata missing: %s",
                user_id,
                ", ".join(e.missing_keys),
            )
            await self._insert_default_metadata(user_orm, e.missing_keys)
            user_domain = user_orm_to_domain(user_orm)
            logger.info("User %d retrieved after metadata fix", user_id)
            return user_domain

    async def update_metadata(self, user: "User", key: str, value: Any) -> None:
        """Обновление метаданных пользователя"""
        logger.debug("Updating metadata %s for user %d", key, user.user_id)
        old_metadata_value = user.metadata.get(key)
        user.update_metadata(key, value)

        stmt = (
            update(UserMetadataORM)
            .where(UserMetadataORM.user_id == user.user_id, UserMetadataORM.key == key)
            .values(value=json.dumps(value, ensure_ascii=False))
        )

        try:
            await self.session.execute(stmt)
            logger.info("Metadata %s for user %d updated", key, user.user_id)
        except (SQLAlchemyError, IntegrityError, TimeoutError):
            logger.exception(
                "Failed to update metadata %s for user %d",
                key,
                user.user_id,
            )
            user.metadata[key] = old_metadata_value
            raise

    async def subscribe_group(self, user: "User", group: "Group") -> None:
        """Подписка на кабинет"""
        logger.debug("Subscribing user %d to group %s", user.user_id, group.number)
        stmt = (
            insert(GroupSubscribesORM)
            .values(user_id=user.user_id, group_index=group.index)
            .on_conflict_do_nothing()
            .returning(GroupSubscribesORM.group_index)
        )
        inserted = await self.session.scalar(stmt)

        if inserted is None:
            logger.warning(
                "User %d already subscribed to group %s",
                user.user_id,
                group.number,
            )
            raise GroupAlreadyInsertedError(group.number)

        user.group_subscribes = [*user.group_subscribes, group.index]
        logger.info("User %d subscribed to group %s", user.user_id, group.number)

    async def subscribe_cabinet(self, user: "User", cabinet: "Cabinet") -> None:
        """Подписка на кабинет"""
        logger.debug("Subscribing user %d to cabinet %s", user.user_id, cabinet.number)
        stmt = (
            insert(CabinetSubscribesORM)
            .values(user_id=user.user_id, cabinet_index=cabinet.index)
            .on_conflict_do_nothing()
            .returning(CabinetSubscribesORM.cabinet_index)
        )
        inserted = await self.session.scalar(stmt)

        if inserted is None:
            logger.warning(
                "User %d already subscribed to cabinet %s",
                user.user_id,
                cabinet.number,
            )
            raise CabinetAlreadyInsertedError(cabinet.number)

        user.cabinet_subscribes = [*user.cabinet_subscribes, cabinet.index]
        logger.info("User %d subscribed to cabinet %s", user.user_id, cabinet.number)

    async def unsubscribe_group(self, user: "User", group_index: str) -> None:
        """Отписка от группы"""
        logger.debug("Unsubscribing user %d from group %s", user.user_id, group_index)

        if group_index not in user.group_subscribes:
            logger.warning(
                "User %d not subscribed to group %s",
                user.user_id,
                group_index,
            )
            raise GroupUnsubscribeNotFoundError()

        stmt = delete(GroupSubscribesORM).where(
            GroupSubscribesORM.user_id == user.user_id,
            GroupSubscribesORM.group_index == group_index,
        )
        await self.session.execute(stmt)

        user.group_subscribes = [g for g in user.group_subscribes if g != group_index]
        logger.info("User %d unsubscribed from group %s", user.user_id, group_index)

    async def unsubscribe_cabinet(self, user: "User", cabinet_index: str) -> None:
        """Отписка от кабинета"""
        logger.debug(
            "Unsubscribing user %d from cabinet %s",
            user.user_id,
            cabinet_index,
        )

        if cabinet_index not in user.cabinet_subscribes:
            logger.warning(
                "User %d not subscribed to cabinet %s",
                user.user_id,
                cabinet_index,
            )
            raise CabinetUnsubscribeNotFoundError()

        stmt = delete(CabinetSubscribesORM).where(
            CabinetSubscribesORM.user_id == user.user_id,
            CabinetSubscribesORM.cabinet_index == cabinet_index,
        )
        await self.session.execute(stmt)

        user.cabinet_subscribes = [
            c for c in user.cabinet_subscribes if c != cabinet_index
        ]
        logger.info("User %d unsubscribed from cabinet %s", user.user_id, cabinet_index)

    async def _insert_default_metadata(
        self,
        user_orm: "UserORM",
        keys: Iterable[str],
    ) -> None:
        """Вставка стандартных метаданных"""
        logger.debug("Inserting default metadata for user %d", user_orm.user_id)
        keys_to_add = {key for key in keys if key in User._REQUIRED_METADATA}

        if not keys_to_add:
            logger.debug("No default metadata to insert for user %d", user_orm.user_id)
            return

        for key in keys_to_add:
            user_orm.user_metadata.append(
                UserMetadataORM(
                    key=key,
                    value=json.dumps(User._DEFAULT_METADATA[key], ensure_ascii=False),
                ),
            )

        logger.info(
            "Default metadata inserted for user %d: %s",
            user_orm.user_id,
            ", ".join(keys_to_add),
        )
