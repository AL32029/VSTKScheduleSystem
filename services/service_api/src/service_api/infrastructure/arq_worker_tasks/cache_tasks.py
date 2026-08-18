from collections.abc import Iterable
from typing import Literal

from dishka import AsyncContainer

from service_api.application.ports import CacheRepository
from service_api.infrastructure.arq_worker_tasks.config import _dishka_container


async def clear_cache(
    ctx,  # noqa: ARG001
    group_keys: Iterable[str],
    cabinet_keys: Iterable[str],
    group_schedules: dict[Literal["today", "tomorrow"], Iterable[str]],
    cabinet_schedules: dict[Literal["today", "tomorrow"], Iterable[str]],
):
    container: AsyncContainer = _dishka_container

    cache_repository: CacheRepository = await container.get(CacheRepository)

    if group_keys:
        await cache_repository.delete_group_cache(group_keys)

    if cabinet_keys:
        await cache_repository.delete_cabinet_cache(cabinet_keys)

    if group_schedules:
        await cache_repository.delete_group_day_schedule_cache(group_schedules)

    if cabinet_schedules:
        await cache_repository.delete_cabinet_day_schedule_cache(cabinet_schedules)

    return "Items was removed successfully"
