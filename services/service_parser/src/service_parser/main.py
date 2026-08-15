import asyncio
import logging.config
from zoneinfo import ZoneInfo

import time
from httpx import AsyncClient
from redis.asyncio import Redis

from service_parser.application.ports import (
    CabinetRepository,
    GroupRepository,
    ScheduleRepository,
)
from service_parser.application.services import ScheduleParserUseCase
from service_parser.infrastructure.clients import HTTPXScheduleProvider
from service_parser.infrastructure.config import LoggingSettings
from service_parser.infrastructure.di.container import get_dishka_container

logging.config.dictConfig(LoggingSettings().model_dump(mode='json'))

logger = logging.getLogger('service_parser')

container = get_dishka_container()


async def main():
    logger.info('Starting schedule parser cron job')
    start_time = time.perf_counter()

    try:
        async with container() as cont:
            client = await cont.get(AsyncClient)
            redis_client = await cont.get(Redis)

            group_repo = await cont.get(GroupRepository)
            cabinet_repo = await cont.get(CabinetRepository)
            day_schedule_repo = await cont.get(ScheduleRepository)
            timezone = await cont.get(ZoneInfo)

            for schedule_type in ['today', 'tomorrow']:
                logger.info('Processing schedule for %s', schedule_type)
                type_start = time.perf_counter()

                provider = HTTPXScheduleProvider(
                    client=client,
                    redis_client=redis_client,
                    schedule_type=schedule_type,
                    timezone=timezone
                )
                use_case = ScheduleParserUseCase(
                    group_repo,
                    cabinet_repo,
                    day_schedule_repo,
                    provider
                )

                try:
                    await use_case.execute()
                    duration = (time.perf_counter() - type_start) * 1000
                    logger.info('Schedule for %s processed successfully (%.2f ms)', schedule_type, duration)
                except Exception:
                    logger.exception('Failed to process schedule for %s', schedule_type)
                    continue

            total_duration = (time.perf_counter() - start_time) * 1000
            logger.info('Schedule parser cron job completed (%.2f ms)', total_duration)

    except Exception:
        logger.exception('Fatal error in schedule parser cron job')
        raise


if __name__ == '__main__':
    asyncio.run(main())
