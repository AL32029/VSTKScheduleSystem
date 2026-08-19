import asyncio
import logging
import random
from collections.abc import Iterable
from datetime import date
from itertools import batched
from typing import Literal

from aiogram import Bot
from aiogram.exceptions import AiogramError
from dishka import Scope
from sqlalchemy import and_, exists, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncScalarResult, AsyncSession

from service_bot.application.ports import CabinetRepository, GroupRepository
from service_bot.domain.entities import Cabinet, Group
from service_bot.domain.exceptions import UserMetadataMissingError
from service_bot.domain.exceptions.base_exceptions import BotServiceError
from service_bot.infrastructure.db import (
    CabinetSubscribesORM,
    GroupSubscribesORM,
    UserMetadataORM,
    UserORM,
)
from service_bot.infrastructure.db.mappers import user_orm_to_domain
from service_bot.infrastructure.template_engine_items import (
    TemplateKeyboardRenderer,
    TemplateMessageRenderer,
)

from .config import _dishka_container, _rate_limiter

logger = logging.getLogger(__name__)


async def notify_users(
    ctx,  # noqa: ARG001
    changes: dict[
        Literal["group", "cabinet"],
        dict[Literal["new", "update", "remove"], Iterable[str]],
    ],
    schedule_to: Literal["today", "tomorrow"],
    dates: date | tuple[date, date],
):
    logger.info(
        "Starting notification process for %s",
        schedule_to,
    )

    _group_changes: dict[Literal["new", "update", "remove"], Iterable[str]] = (
        changes.get("group", {})
    )
    _group_new = set(_group_changes.get("new", set()))
    _group_update = set(_group_changes.get("update", set()))
    _group_remove = set(_group_changes.get("remove", set()))

    _cabinet_changes: dict[Literal["new", "update", "remove"], Iterable[str]] = (
        changes.get("cabinet", {})
    )
    _cabinet_new = set(_cabinet_changes.get("new", set()))
    _cabinet_update = set(_cabinet_changes.get("update", set()))
    _cabinet_remove = set(_cabinet_changes.get("remove", set()))

    logger.debug(
        "Changes extracted: groups(new=%d, update=%d, remove=%d), "
        "cabinets(new=%d, update=%d, remove=%d)",
        len(_group_new),
        len(_group_update),
        len(_group_remove),
        len(_cabinet_new),
        len(_cabinet_update),
        len(_cabinet_remove),
    )

    _users_to_notify: list[
        tuple[
            int,
            Literal["group", "cabinet"],
            Iterable[str],
            Literal["new", "update", "remove"],
            Literal["today", "tomorrow"],
        ]
    ] = []

    async with _dishka_container(scope=Scope.REQUEST) as _container:
        _db = await _container.get(AsyncSession)
        _group_repo = await _container.get(GroupRepository)
        _cabinet_repo = await _container.get(CabinetRepository)

        stmt = select(UserORM).where(
            and_(
                exists().where(
                    and_(
                        UserMetadataORM.user_id == UserORM.user_id,
                        UserMetadataORM.key == "notifications_enabled",
                        UserMetadataORM.value == "true",
                    )
                ),
                or_(
                    and_(
                        exists().where(
                            and_(
                                UserMetadataORM.user_id == UserORM.user_id,
                                UserMetadataORM.key == "user_type",
                                UserMetadataORM.value == '"student"',
                            )
                        ),
                        exists().where(GroupSubscribesORM.user_id == UserORM.user_id),
                    ),
                    and_(
                        exists().where(
                            and_(
                                UserMetadataORM.user_id == UserORM.user_id,
                                UserMetadataORM.key == "user_type",
                                UserMetadataORM.value == '"teacher"',
                            )
                        ),
                        exists().where(CabinetSubscribesORM.user_id == UserORM.user_id),
                    ),
                ),
            )
        )

        _result: AsyncScalarResult[UserORM] = await _db.stream_scalars(stmt)

        _processed_users = 0
        async for _user_db in _result:
            _processed_users += 1
            try:
                _user = user_orm_to_domain(_user_db)
                logger.debug(
                    "User entity with ID %s has been initialized", _user.user_id
                )
            except UserMetadataMissingError:
                logger.warning(
                    "User with ID %s is missing part of the metadata. "
                    "Perhaps the user hasn’t used the bot in a long time",
                    _user_db.user_id,
                )
                continue
            except (SQLAlchemyError, BotServiceError):
                logger.exception("Error when receiving user information")
                continue

            if _user.user_type == "student" and _user.group_subscribes:
                _subscribes = set(_user.group_subscribes)

                if _new_groups := _subscribes & _group_new:
                    _users_to_notify.append(
                        (_user.user_id, "group", _new_groups, "new", schedule_to)
                    )
                    logger.debug(
                        "User %s: new groups %s",
                        _user.user_id,
                        _new_groups,
                    )

                if _update_groups := _subscribes & _group_update:
                    _users_to_notify.append(
                        (_user.user_id, "group", _update_groups, "update", schedule_to)
                    )
                    logger.debug(
                        "User %s: updated groups %s",
                        _user.user_id,
                        _update_groups,
                    )

                if _remove_groups := _subscribes & _group_remove:
                    _users_to_notify.append(
                        (_user.user_id, "group", _remove_groups, "remove", schedule_to)
                    )
                    logger.debug(
                        "User %s: removed groups %s",
                        _user.user_id,
                        _remove_groups,
                    )

            if _user.user_type == "teacher" and _user.cabinet_subscribes:
                _subscribes = set(_user.cabinet_subscribes)

                if _new_cabinets := _subscribes & _cabinet_new:
                    _users_to_notify.append(
                        (_user.user_id, "cabinet", _new_cabinets, "new", schedule_to)
                    )
                    logger.debug(
                        "User %s: new cabinets %s",
                        _user.user_id,
                        _new_cabinets,
                    )

                if _update_cabinets := _subscribes & _cabinet_update:
                    _users_to_notify.append(
                        (
                            _user.user_id,
                            "cabinet",
                            _update_cabinets,
                            "update",
                            schedule_to,
                        )
                    )
                    logger.debug(
                        "User %s: updated cabinets %s",
                        _user.user_id,
                        _update_cabinets,
                    )

                if _remove_cabinets := _subscribes & _cabinet_remove:
                    _users_to_notify.append(
                        (
                            _user.user_id,
                            "cabinet",
                            _remove_cabinets,
                            "remove",
                            schedule_to,
                        )
                    )
                    logger.debug(
                        "User %s: removed cabinets %s",
                        _user.user_id,
                        _remove_cabinets,
                    )

        logger.info(
            "Processed %d eligible users, generated %d notification tasks",
            _processed_users,
            len(_users_to_notify),
        )

        if _users_to_notify:
            _message_templater = await _container.get(TemplateMessageRenderer)
            _keyboard_templater = await _container.get(TemplateKeyboardRenderer)
            _bot_client = await _container.get(Bot)
            _all_groups = await _group_repo.get_all()
            _all_cabinets = await _cabinet_repo.get_all()

            batches = list(batched(_users_to_notify, 50))
            logger.info(
                "Sending notifications in %d batches (max 50 tasks per batch)",
                len(batches),
            )

            await asyncio.gather(
                *[
                    asyncio.create_task(
                        _send_notifications_batch(
                            _notifications,
                            _bot_client,
                            _all_groups,
                            _all_cabinets,
                            _message_templater,
                            _keyboard_templater,
                            dates,
                        )
                    )
                    for _notifications in batches
                ]
            )

            logger.info("All notification batches have been processed")
        else:
            logger.info("No users to notify for %s", schedule_to)

    logger.info("Notification process for %s completed", schedule_to)
    return "Users have been successfully notified"


async def _send_notifications_batch(
    batch_items: Iterable[
        tuple[
            int,
            Literal["group", "cabinet"],
            Iterable[str],
            Literal["new", "update", "remove"],
            Literal["today", "tomorrow"],
        ]
    ],
    bot_client: Bot,
    groups: Iterable["Group"],
    cabinets: Iterable["Cabinet"],
    message_templater: "TemplateMessageRenderer",
    keyboard_templater: "TemplateKeyboardRenderer",
    dates: date | tuple[date, date],
):
    _dates = (dates,) if not isinstance(dates, tuple) else dates
    _batch_list = list(batch_items)
    _button = keyboard_templater.delete_message()
    logger.debug("Processing batch of %d notification tasks", len(_batch_list))

    for _user_id, _item_type, _items, _action, _schedule_to in _batch_list:
        async with _rate_limiter:
            if _item_type == "group":
                entities = [g.number for g in groups if g.index in _items]
            else:
                entities = [c.number for c in cabinets if c.index in _items]

            message_text = message_templater.render(
                "schedule_notification",
                schedule_item_type=_item_type,
                schedule_items=entities,
                action=_action,
                schedule_to=_schedule_to,
                dates=_dates,
            )

            try:
                logger.debug(
                    "Sending notification to user %s: %s %s %s (items: %s)",
                    _user_id,
                    _item_type,
                    _action,
                    _schedule_to,
                    entities,
                )
                await bot_client.send_message(
                    chat_id=_user_id, text=message_text, reply_markup=_button
                )
                logger.debug(
                    "Notification successfully sent to user %s",
                    _user_id,
                )
            except AiogramError as e:
                logger.warning(
                    "Failed to send notification to user %s: %s",
                    _user_id,
                    e,
                )
            else:
                delay = random.uniform(0.1, 0.75)
                logger.debug("Sleeping for %.2f s before next message", delay)
                await asyncio.sleep(delay)

    logger.debug("Batch processing completed")
