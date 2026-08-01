from typing import Literal

from service_api.application.ports import GroupRepository, ScheduleRepository
from service_api.domain.entities import GroupDaySchedule


class GetGroupDayScheduleUseCase:
    def __init__(self, group_repo: GroupRepository, schedule_repo: ScheduleRepository):
        self.schedule_repo = schedule_repo
        self.group_repo = group_repo

    async def execute(self, group_number: str, schedule_to: Literal['today', 'tomorrow']) -> GroupDaySchedule:
        group_item = await self.group_repo.get_by_number(group_number)

        schedule_date = await self.schedule_repo.get_schedule_date(schedule_to)

        day_schedule = await self.schedule_repo.get_by_group(group_item, schedule_date)

        return day_schedule
