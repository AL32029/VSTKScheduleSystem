from itertools import chain

from service_parser.application.ports import GroupRepository, CabinetRepository, ScheduleRepository, ScheduleProvider
from service_parser.domain.entities import Group, DaySchedule
from service_parser.domain.exceptions.parser_exceptions import ScheduleUnchangedError


class ScheduleParserUseCase:
    def __init__(self, group_repo: 'GroupRepository', cabinet_repo: 'CabinetRepository',
                 schedule_repo: 'ScheduleRepository', schedule_provider: 'ScheduleProvider') -> None:
        self.group_repo = group_repo
        self.cabinet_repo = cabinet_repo
        self.schedule_repo = schedule_repo
        self.schedule_provider = schedule_provider

    async def execute(self) -> None:
        try:
            schedule = await self.schedule_provider.get_schedule_for_groups()
        except ScheduleUnchangedError:
            return

        if not schedule:
            return

        await self._save_metadata(schedule)
        await self.schedule_repo.save(list(chain.from_iterable(schedule.values())))

    async def _save_metadata(self, schedule: dict['Group', list['DaySchedule']]) -> None:
        await self.group_repo.save(schedule.keys())

        cabinets = {cabinet
                    for day_schedule in chain.from_iterable(schedule.values())
                    if day_schedule.lessons
                    for lesson in day_schedule.lessons if lesson.cabinets
                    for cabinet in lesson.cabinets}
        if cabinets:
            await self.cabinet_repo.save(cabinets)
