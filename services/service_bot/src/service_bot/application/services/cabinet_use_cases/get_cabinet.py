import logging

from service_bot.application.ports import CabinetRepository
from service_bot.domain.entities import Cabinet

logger = logging.getLogger(__name__)


class GetCabinetUseCase:
    """UseCase получения кабинета"""

    def __init__(self, repo: "CabinetRepository"):
        self.repo = repo

    async def execute(self, cabinet_number: str) -> "Cabinet":
        logger.info("Obtaining information about cabinet %s", cabinet_number)
        cabinet_item = await self.repo.get_by_number(cabinet_number)
        logger.info("Information has been received about cabinet %s", str(cabinet_item))

        return cabinet_item
