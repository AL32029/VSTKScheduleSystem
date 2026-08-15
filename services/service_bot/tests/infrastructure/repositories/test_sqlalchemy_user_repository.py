import random
from typing import cast

import pytest

from service_bot.domain.entities import User
from service_bot.domain.exceptions import (
    CabinetAlreadyInsertedError,
    CabinetUnsubscribeNotFoundError,
    GroupAlreadyInsertedError,
    GroupUnsubscribeNotFoundError,
    UserNotFoundError,
)
from tests.test_contains import _CABINET_ITEM, _GROUP_ITEM, _USER_ID


async def test_user_save(sqlalchemy_user_repo):
    user_item = await sqlalchemy_user_repo.save(_USER_ID)

    assert isinstance(user_item, User)
    assert user_item.user_id == _USER_ID
    assert user_item.metadata == User._DEFAULT_METADATA


async def test_user_get_by_id(sqlalchemy_user_repo, saved_user):  # noqa: ARG001
    user_item = await sqlalchemy_user_repo.get_by_id(_USER_ID)

    assert isinstance(user_item, User)
    assert user_item.user_id == _USER_ID
    assert user_item.metadata == User._DEFAULT_METADATA


async def test_user_get_by_id_error_not_found(sqlalchemy_user_repo):
    with pytest.raises(UserNotFoundError) as exc_info:
        await sqlalchemy_user_repo.get_by_id(_USER_ID)

    assert exc_info.value.args[0] == f"User with ID {_USER_ID} not found"


async def test_user_get_by_id_without_metadata(
    sqlalchemy_user_repo, saved_user_without_metadata,
):
    user_before, deleted_metadata = saved_user_without_metadata

    assert deleted_metadata not in user_before.metadata

    user = await sqlalchemy_user_repo.get_by_id(user_before.user_id)

    assert deleted_metadata in user.metadata


async def test_user_update_metadata(sqlalchemy_user_repo, saved_user):
    old_metadata_value: None = cast("None", saved_user.message_panel_id)

    new_value = random.randint(1, 999)

    await sqlalchemy_user_repo.update_metadata(
        saved_user, "message_panel_id", new_value,
    )

    assert saved_user.message_panel_id is not None
    assert saved_user.message_panel_id != old_metadata_value
    assert saved_user.message_panel_id == new_value


async def test_user_subscribe_group(sqlalchemy_user_repo, saved_user):
    await sqlalchemy_user_repo.subscribe_group(saved_user, _GROUP_ITEM)

    assert _GROUP_ITEM.index in saved_user.group_subscribes


async def test_user_subscribe_group_error_already_inserted(
    sqlalchemy_user_repo, saved_user_with_subscribed_group,
):
    with pytest.raises(GroupAlreadyInsertedError) as exc_info:
        await sqlalchemy_user_repo.subscribe_group(
            saved_user_with_subscribed_group, _GROUP_ITEM,
        )

    assert exc_info.value.args[0] == str(GroupAlreadyInsertedError(_GROUP_ITEM.number))


async def test_user_subscribe_cabinet(sqlalchemy_user_repo, saved_user):
    await sqlalchemy_user_repo.subscribe_group(saved_user, _CABINET_ITEM)

    assert _CABINET_ITEM.index in saved_user.group_subscribes


async def test_user_subscribe_cabinet_error_already_inserted(
    sqlalchemy_user_repo, saved_user_with_subscribed_cabinet,
):
    with pytest.raises(CabinetAlreadyInsertedError) as exc_info:
        await sqlalchemy_user_repo.subscribe_cabinet(
            saved_user_with_subscribed_cabinet, _CABINET_ITEM,
        )

    assert exc_info.value.args[0] == str(
        CabinetAlreadyInsertedError(_CABINET_ITEM.number),
    )


async def test_user_unsubscribe_group(
    sqlalchemy_user_repo, saved_user_with_subscribed_group,
):
    await sqlalchemy_user_repo.unsubscribe_group(
        saved_user_with_subscribed_group, _GROUP_ITEM.index,
    )

    assert _GROUP_ITEM.index not in saved_user_with_subscribed_group.group_subscribes


async def test_user_unsubscribe_group_error_subscribe_not_found(
    sqlalchemy_user_repo, saved_user,
):
    with pytest.raises(GroupUnsubscribeNotFoundError) as exc_info:
        await sqlalchemy_user_repo.unsubscribe_group(saved_user, _GROUP_ITEM)

    assert exc_info.value.args[0] == str(GroupUnsubscribeNotFoundError())


async def test_user_unsubscribe_cabinet(
    sqlalchemy_user_repo, saved_user_with_subscribed_cabinet,
):
    await sqlalchemy_user_repo.unsubscribe_cabinet(
        saved_user_with_subscribed_cabinet, _CABINET_ITEM.index,
    )

    assert (
        _CABINET_ITEM.index not in saved_user_with_subscribed_cabinet.group_subscribes
    )


async def test_user_unsubscribe_cabinet_error_subscribe_not_found(
    sqlalchemy_user_repo, saved_user,
):
    with pytest.raises(CabinetUnsubscribeNotFoundError) as exc_info:
        await sqlalchemy_user_repo.unsubscribe_cabinet(saved_user, _CABINET_ITEM)

    assert exc_info.value.args[0] == str(CabinetUnsubscribeNotFoundError())
