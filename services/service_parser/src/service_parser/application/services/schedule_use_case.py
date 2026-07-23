import datetime
from typing import Iterable

from service_parser.application.ports import ScheduleRepository
from service_parser.domain.entities import DaySchedule, Group, Lesson


class ScheduleUseCase:
    def __init__(self, schedule_repo: ScheduleRepository):
        self.repo = schedule_repo


class CreateDayScheduleUseCase(ScheduleUseCase):
    async def execute(self, group: str | Group, schedule_date: datetime.date, lessons: Iterable[Lesson]) -> DaySchedule:
        day_schedule = DaySchedule.from_existing(schedule_date, group, lessons)

        await self.repo.save(day_schedule)

        return day_schedule


class CreateManyDaySchedulesUseCase(ScheduleUseCase):
    async def execute(self, day_schedules: Iterable[DaySchedule]) -> Iterable[DaySchedule]:
        await self.repo.save_all(day_schedules)

        return day_schedules


class GetDayScheduleByGroupUseCase(ScheduleUseCase):
    async def execute(self, group: str | Group, schedule_date: datetime.date) -> DaySchedule:
        day_schedule = await self.repo.get_by_group(group if isinstance(group, Group) else Group(group), schedule_date)

        return day_schedule
