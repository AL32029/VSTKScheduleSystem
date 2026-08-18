from collections.abc import Iterable

from service_parser.application.ports import (
    CabinetRepository,
    GroupRepository,
    ScheduleProvider,
    ScheduleRepository,
)
from service_parser.domain.entities import Cabinet, DaySchedule, Group
from service_parser.domain.exceptions import ScheduleUnchangedError


class ScheduleParserUseCase:
    def __init__(
        self,
        group_repo: "GroupRepository",
        cabinet_repo: "CabinetRepository",
        schedule_repo: "ScheduleRepository",
        schedule_provider: "ScheduleProvider",
    ) -> None:
        self.group_repo = group_repo
        self.cabinet_repo = cabinet_repo
        self.schedule_repo = schedule_repo
        self.schedule_provider = schedule_provider

    async def execute(self) -> None:
        try:
            schedule, date_list = await self.schedule_provider.get_schedule_for_groups()
        except ScheduleUnchangedError:
            return

        if not schedule:
            return

        await self._save_metadata(schedule)
        await self.schedule_repo.save(list(schedule.values()), date_list)

    async def _save_metadata(self, schedule: dict["Group", "DaySchedule"]) -> None:
        await self._update_groups(schedule.keys())
        await self._insert_cabinets(schedule.values())

    async def _update_groups(self, groups: Iterable["Group"]):
        groups_schedule = set(groups)
        groups_db = set(await self.group_repo.get_many(groups))

        if to_save := groups_schedule - groups_db:
            await self.group_repo.save(to_save)

        if to_deactivate := groups_db - groups_schedule:
            await self.group_repo.deactivate(to_deactivate)

    async def _insert_cabinets(self, day_schedules: Iterable["DaySchedule"]):
        cabinets: set[Cabinet] = {
            cabinet
            for day_schedule in day_schedules
            if day_schedule.lessons
            for lesson in day_schedule.lessons
            if lesson.cabinets
            for cabinet in lesson.cabinets
        }

        if cabinets:
            await self.cabinet_repo.save(cabinets)
