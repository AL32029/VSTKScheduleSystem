from typing import Literal

from service_api.application.ports import CabinetRepository, ScheduleRepository
from service_api.domain.entities import CabinetDaySchedule


class GetCabinetDayScheduleUseCase:
    def __init__(self, cabinet_repo: CabinetRepository, schedule_repo: ScheduleRepository):
        self.schedule_repo = schedule_repo
        self.group_repo = cabinet_repo

    async def execute(self, cabinet_number: str, schedule_to: Literal['today', 'tomorrow']) -> CabinetDaySchedule:
        cabinet_item = await self.group_repo.get_by_number(cabinet_number)

        schedule_date = await self.schedule_repo.get_schedule_date(schedule_to)

        day_schedule = await self.schedule_repo.get_by_cabinet(cabinet_item, schedule_date)

        return day_schedule
