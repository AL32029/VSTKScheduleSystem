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


class HTTPXScheduleRepository(ScheduleRepository):
    """Репозиторий HTTPXScheduleRepository [Реализация репозитория ScheduleRepository]"""
    def __init__(self, client: 'AsyncClient'):
        self.client = client

    async def get_day_schedule(self, schedule_item: str, schedule_to: Literal['today', 'tomorrow'],
                               schedule_for: Literal['group', 'cabinet']) -> 'DaySchedule':
        """Получение расписания на конкретную дату"""
        resp = await self.client.get(f'{self.client.base_url}/schedule/{schedule_for}', params={
            f'{schedule_for}_number': schedule_item,
            'schedule_to': schedule_to
        })

        try:
            resp.raise_for_status()
        except HTTPStatusError as e:
            if e.response.is_server_error:
                raise

            if e.response.status_code == 404:
                if schedule_for == 'group' and str(e) == f'Group with number {schedule_item!r} not found':
                    raise GroupNotFound(schedule_item)
                elif schedule_for == 'cabinet' and str(e) == f'Cabinet with number {schedule_item!r} not found':
                    raise CabinetNotFound(schedule_item)
                elif f'database does not contain a schedule date for {schedule_to}' in str(e):
                    raise ScheduleDateNotFound(schedule_item, schedule_to)
                elif f'database does not contain a schedule date for {schedule_item}' in str(e):
                    if schedule_for == 'group':
                        raise ScheduleForGroupNotFound(schedule_to)

                    raise ScheduleForCabinetNotFound(schedule_to)

            raise

        day_schedule = DayScheduleItem.model_validate(resp.json())

        return day_schedule.to_domain(schedule_for)
