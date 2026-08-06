from service_bot.application.ports import UserRepository
from service_bot.domain.entities import User
from service_bot.domain.exceptions.bot_exceptions import UserNotFound


class GetUserProfileUseCase:
    """UseCase получения профиля пользователя"""
    def __init__(self, repo: 'UserRepository'):
        self.repo = repo

    async def execute(self, user_id: int) -> 'User':
        try:
            user = await self.repo.get_by_id(user_id)
        except UserNotFound:
            raise

        return user