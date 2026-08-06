from service_bot.application.ports import UserRepository
from service_bot.domain.entities import User


class SaveUserProfileUseCase:
    """UseCase сохранения профиля пользователя"""
    def __init__(self, repo: 'UserRepository'):
        self.repo = repo

    async def execute(self, user_id: int) -> 'User':
        user = await self.repo.save(user_id)

        return user