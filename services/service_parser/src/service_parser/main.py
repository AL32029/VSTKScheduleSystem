import asyncio
import logging
import sys
import time
from itertools import chain

from dishka import Scope
from httpx import AsyncClient

from service_parser.application.ports import GroupRepository, CabinetRepository, ScheduleRepository
from service_parser.infrastructure.clients import HTTPXScheduleProvider
from service_parser.infrastructure.di.container import get_dishka_container

logging.basicConfig(level=logging.CRITICAL, stream=sys.stdout)


# TODO: Добавить тесты
# [MISC][INPROGRESS] Настроить зависимости (Dishka)
# TODO: Реализовать функции для выполнения CronJob

async def main():
    container = get_dishka_container()
    async with container(scope=Scope.REQUEST) as cont:
        client = await cont.get(AsyncClient)
        group_repo = await cont.get(GroupRepository)
        cabinet_repo = await cont.get(CabinetRepository)
        day_schedule_repo = await cont.get(ScheduleRepository)

    provider = HTTPXScheduleProvider(client, 'tomorrow')

    schedule = await provider.get_schedule_for_groups(url='https://vgtk.by/schedule/lessons/day-tomorrow.php')

    groups_db = await group_repo.get_all()
    group_to_add = {
        group for group in schedule.keys() if group not in groups_db
    }

    if group_to_add:
        await group_repo.save_all(group_to_add)

    cabinets = {
        cabinet
        for day_schedules in schedule.values()
        for day_schedule in day_schedules if day_schedule.lessons
        for lesson in day_schedule.lessons if lesson.cabinets
        for cabinet in lesson.cabinets
    }

    cabinets_db = await cabinet_repo.get_all()
    cabinets_to_add = {cabinet for cabinet in cabinets if cabinet not in cabinets_db}

    if cabinets_to_add:
        await cabinet_repo.save_all(cabinets_to_add)

    start = time.perf_counter()
    if schedule.values():
        await day_schedule_repo.save_all(tuple(chain.from_iterable(schedule.values())))
    end = time.perf_counter()

    print(end - start)


if __name__ == '__main__':
    asyncio.run(main())
