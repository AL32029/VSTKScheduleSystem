from typing import Literal

from service_api.application.ports import (
    CacheRepository,
    GroupRepository,
    ScheduleRepository,
)
from service_api.domain.entities import GroupDaySchedule
from service_api.domain.exceptions import CacheItemNotFound


class GetGroupDayScheduleUseCase:
    def __init__(self, group_repo: 'GroupRepository', schedule_repo: 'ScheduleRepository',
                 cache_repo: 'CacheRepository'):
        self.schedule_repo = schedule_repo
        self.group_repo = group_repo
        self.cache_repo = cache_repo

    async def execute(self, group_number: str, schedule_to: Literal['today', 'tomorrow']) -> 'GroupDaySchedule':
        try:
            day_schedule = await self.cache_repo.get_group_day_schedule(schedule_to, group_number)
        except CacheItemNotFound:
            group_item = await self.group_repo.get_by_number(group_number)

            schedule_date = await self.schedule_repo.get_schedule_date(schedule_to)

            day_schedule = await self.schedule_repo.get_by_group(group_item, schedule_to, schedule_date)

            await self.cache_repo.set_group_day_schedule(schedule_to, day_schedule)

        return day_schedule
