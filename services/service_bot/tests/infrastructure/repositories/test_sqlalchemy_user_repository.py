from service_bot.domain.entities import User
from tests.test_contains import _USER_ID


async def test_user_save(sqlalchemy_user_repo):
    user_item = await sqlalchemy_user_repo.save(_USER_ID)

    assert isinstance(user_item, User)
    assert user_item.user_id == _USER_ID
    assert user_item.metadata == User._DEFAULT_METADATA

# TODO: Дописать тесты для SQLAlchemyUserRepository
