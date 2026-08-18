from collections.abc import Iterable
from typing import Literal

from arq import ArqRedis
from dishka import Scope

from service_parser.infrastructure.di.container import get_dishka_container

_container = get_dishka_container()


async def send_clear_cache_task(
    group_keys: Iterable[str],
    cabinet_keys: Iterable[str],
    group_schedules: dict[Literal["today", "tomorrow"], Iterable[str]],
    cabinet_schedules: dict[Literal["today", "tomorrow"], Iterable[str]],
):
    async with _container(scope=Scope.REQUEST) as container:
        pool = await container.get(ArqRedis, component="redis_arq")
        await pool.enqueue_job(
            "clear_cache",
            group_keys=group_keys,
            cabinet_keys=cabinet_keys,
            group_schedules=group_schedules,
            cabinet_schedules=cabinet_schedules,
            _queue_name="cache",
        )
