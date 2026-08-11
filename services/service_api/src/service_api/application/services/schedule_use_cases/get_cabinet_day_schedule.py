from typing import Literal

from service_api.application.ports import (
    CabinetRepository,
    CacheRepository,
    ScheduleRepository,
)
from service_api.domain.entities import CabinetDaySchedule
from service_api.domain.exceptions import CacheItemNotFound


class GetCabinetDayScheduleUseCase:
    def __init__(self, cabinet_repo: 'CabinetRepository', schedule_repo: 'ScheduleRepository',
                 cache_repo: 'CacheRepository'):
        self.schedule_repo = schedule_repo
        self.group_repo = cabinet_repo
        self.cache_repo = cache_repo

    async def execute(self, cabinet_number: str, schedule_to: Literal['today', 'tomorrow']) -> 'CabinetDaySchedule':
        try:
            day_schedule = await self.cache_repo.get_cabinet_day_schedule(cabinet_number, schedule_to)
        except CacheItemNotFound:
            cabinet_item = await self.group_repo.get_by_number(cabinet_number)

            schedule_date = await self.schedule_repo.get_schedule_date(schedule_to)

            day_schedule = await self.schedule_repo.get_by_cabinet(cabinet_item, schedule_to, schedule_date)

            await self.cache_repo.set_cabinet_day_schedule(schedule_to, day_schedule)

        return day_schedule
