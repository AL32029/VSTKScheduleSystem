from collections.abc import Iterable
from datetime import date
from typing import Literal

from service_parser.application.ports import (
    CabinetRepository,
    GroupRepository,
    ScheduleProvider,
    ScheduleRepository,
    TasksRepository,
)
from service_parser.domain.entities import Cabinet, DaySchedule, Group
from service_parser.domain.exceptions import ScheduleUnchangedError


class ScheduleParserUseCase:
    def __init__(
        self,
        group_repo: "GroupRepository",
        cabinet_repo: "CabinetRepository",
        schedule_repo: "ScheduleRepository",
        tasks_repo: "TasksRepository",
        schedule_provider: "ScheduleProvider",
    ) -> None:
        self.group_repo = group_repo
        self.cabinet_repo = cabinet_repo
        self.schedule_repo = schedule_repo
        self.tasks_repo = tasks_repo
        self.schedule_provider = schedule_provider

    async def execute(self, schedule_to: Literal["today", "tomorrow"]) -> None:
        try:
            schedule, date_list = await self.schedule_provider.get_schedule_for_groups()
        except ScheduleUnchangedError:
            return

        if not schedule:
            return

        await self._save_metadata(schedule)

        changes = await self.schedule_repo.save(list(schedule.values()), date_list)
        groups_clear, cabinets_clear = self._extract_changed_entities(changes)

        await self.tasks_repo.send_clear_cache_task(
            groups_clear, cabinets_clear, schedule_to
        )

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

    @staticmethod
    def _extract_changed_entities(
        changes: dict[date, dict[str, dict[str, set["Group" | "Cabinet"]]]],
    ) -> tuple[set[str], set[str]]:
        groups = set()
        cabinets = set()

        for entity_changes in changes.values():
            group_data = entity_changes.get("group", {})
            for category in ("new", "update", "remove"):
                for group in group_data.get(category, set()):
                    groups.add(group.index)

            cabinet_data = entity_changes.get("cabinet", {})
            for category in ("new", "update", "remove"):
                for cabinet in cabinet_data.get(category, set()):
                    cabinets.add(cabinet.number)

        return groups, cabinets
