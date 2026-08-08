import logging

from service_bot.application.ports import CabinetRepository
from service_bot.domain.entities import Cabinet

logger = logging.getLogger(__name__)


class GetAllCabinetsUseCase:
    """UseCase получения списка всех кабинетов"""

    def __init__(self, repo: 'CabinetRepository'):
        self.repo = repo

    async def execute(self) -> list['Cabinet']:
        logger.info('Loading the list of cabinets')
        group_items = await self.repo.get_all()
        logger.info('The list of cabinets has been loaded')

        return group_items
