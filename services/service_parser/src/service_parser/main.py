import asyncio
import logging
import sys
import time

from dishka import Scope
from httpx import AsyncClient

from service_parser.application.ports import GroupRepository, CabinetRepository, ScheduleRepository
from service_parser.application.services.schedule_parser_use_case import ParseScheduleUseCase
from service_parser.infrastructure.clients import HTTPXScheduleProvider
from service_parser.infrastructure.di.container import get_dishka_container

logging.basicConfig(level=logging.CRITICAL, stream=sys.stdout)


# [MISC][INPROGRESS][HIGH] Добавить тесты
# [MISC][DONE] Настроить зависимости (Dishka)
# [MISC][INPROGRESS] Реализовать функции для выполнения CronJob

async def main():
    start = time.perf_counter()

    container = get_dishka_container()
    async with container(scope=Scope.REQUEST) as cont:
        client = await cont.get(AsyncClient)
        group_repo = await cont.get(GroupRepository)
        cabinet_repo = await cont.get(CabinetRepository)
        day_schedule_repo = await cont.get(ScheduleRepository)

    provider = HTTPXScheduleProvider(client=client, schedule_type='today')
    schedule_use_case = ParseScheduleUseCase(
        provider,
        group_repo,
        cabinet_repo,
        day_schedule_repo
    )

    schedule = await provider.get_schedule_for_groups()

    end = time.perf_counter()

    print(end - start)


if __name__ == '__main__':
    asyncio.run(main())
