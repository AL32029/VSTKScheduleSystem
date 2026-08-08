import logging
from typing import Literal

from httpx import AsyncClient, HTTPStatusError

from service_bot.application.ports import ScheduleRepository
from service_bot.domain.entities import DaySchedule
from service_bot.domain.exceptions import (
    CabinetNotFound,
    GroupNotFound,
    ScheduleDateNotFound,
    ScheduleForCabinetNotFound,
    ScheduleForGroupNotFound,
)
from service_bot.infrastructure.repositories.schemas import DayScheduleItem

logger = logging.getLogger(__name__)


class HTTPXScheduleRepository(ScheduleRepository):
    """Репозиторий HTTPXScheduleRepository [Реализация репозитория ScheduleRepository]"""

    def __init__(self, client: 'AsyncClient'):
        self.client = client

    async def get_day_schedule(self, schedule_item: str, schedule_to: Literal['today', 'tomorrow'],
                               schedule_for: Literal['group', 'cabinet']) -> 'DaySchedule':
        """Получение расписания на конкретную дату"""
        request = f'/schedule/{schedule_for}'
        resp = await self.client.get(request, params={
            f'{schedule_for}_number': schedule_item,
            'schedule_to': schedule_to
        })

        if resp.status_code == 404:
            if schedule_for == 'group' and resp.text == f'Group with number {schedule_item!r} not found':
                logger.warning('The group %s was not found', schedule_item)
                raise GroupNotFound(schedule_item)
            elif schedule_for == 'cabinet' and resp.text == f'Cabinet with number {schedule_item!r} not found':
                logger.warning('The cabinet %s was not found', schedule_item)
                raise CabinetNotFound(schedule_item)
            elif f'database does not contain a schedule date for {schedule_item} for' in resp.text:
                logger.warning('There are no lessons scheduled for the %s %s for tomorrow',
                               schedule_item, schedule_for)
                raise (ScheduleForGroupNotFound
                       if schedule_for == 'group'
                       else ScheduleForCabinetNotFound)(schedule_to)
            elif f'database does not contain a schedule date for {schedule_to}' in resp.text:
                logger.warning('The schedule date for %s has not been found', schedule_to)
                raise ScheduleDateNotFound(schedule_item, schedule_to)

        try:
            resp.raise_for_status()
        except HTTPStatusError:
            logger.exception('Error when sending an HTTP request GET %s', request)
            raise

        logger.info('A successful response has been received (status: %s)', resp.status_code)

        day_schedule = DayScheduleItem.model_validate(resp.json())

        return day_schedule.to_domain(schedule_for)
