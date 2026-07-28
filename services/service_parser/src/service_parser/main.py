import asyncio
import logging
import sys
import time

from httpx import AsyncClient
from redis.asyncio import Redis

from service_parser.application.ports import GroupRepository, CabinetRepository, ScheduleRepository
from service_parser.application.services import ScheduleParserUseCase
from service_parser.infrastructure.clients import HTTPXScheduleProvider
from service_parser.infrastructure.di.container import get_dishka_container

logging.basicConfig(level=logging.CRITICAL, stream=sys.stdout)

container = get_dishka_container()


async def main():
    start = time.perf_counter()
    async with container() as cont:
        client = await cont.get(AsyncClient)
        redis_client = await cont.get(Redis)

        group_repo = await cont.get(GroupRepository)
        cabinet_repo = await cont.get(CabinetRepository)
        day_schedule_repo = await cont.get(ScheduleRepository)

    for schedule_type in ['today', 'tomorrow']:
        provider = HTTPXScheduleProvider(client=client, redis_client=redis_client, schedule_type=schedule_type)
        use_case = ScheduleParserUseCase(group_repo, cabinet_repo, day_schedule_repo, provider)

        await use_case.execute()

    end = time.perf_counter()

    print(end - start)


if __name__ == '__main__':
    asyncio.run(main())
