import logging

from service_bot.application.ports import GroupRepository
from service_bot.domain.entities import Group

logger = logging.getLogger(__name__)


class GetGroupUseCase:
    """UseCase получения группы"""

    def __init__(self, repo: "GroupRepository"):
        self.repo = repo

    async def execute(self, group_number: str) -> "Group":
        logger.info("Obtaining information about group %s", group_number)
        group_item = await self.repo.get_by_number(group_number)
        logger.info("Information has been received about group %s", str(group_item))

        return group_item
