from itertools import chain
from typing import Iterable

from service_parser.application.ports import ScheduleProvider, CabinetRepository, GroupRepository, ScheduleRepository
from service_parser.domain.entities import DaySchedule


class ParseScheduleUseCase:
    # TODO: Переделать систему с учетом удаления переменной url
    def __init__(self, schedule_provider: ScheduleProvider, group_repo: GroupRepository,
                 cabinet_repo: CabinetRepository, schedule_repo: ScheduleRepository):
        self.schedule_provider = schedule_provider
        self.group_repo = group_repo
        self.cabinet_repo = cabinet_repo
        self.schedule_repo = schedule_repo

    async def execute(self, url: str) -> Iterable[DaySchedule] | None:
        schedule = await self.schedule_provider.get_schedule_for_groups(url)

        if not schedule:
            return None

        groups_db = set(await self.group_repo.get_all())
        groups_schedule = schedule.keys()

        if groups_schedule - groups_db:
            await self.group_repo.save(groups_schedule - groups_db)

        cabinets_db = set(await self.cabinet_repo.get_all())
        cabinets_schedule  = {
            cabinet
            for day_schedule in chain.from_iterable(schedule.values()) if day_schedule.lessons
            for lesson in day_schedule.lessons if lesson.cabinets
            for cabinet in lesson.cabinets
        }

        if cabinets_schedule - cabinets_db:
            await self.cabinet_repo.save(cabinets_schedule - cabinets_db)

        await self.schedule_repo.save(chain.from_iterable(schedule.values()))

        return chain.from_iterable(schedule.values())

