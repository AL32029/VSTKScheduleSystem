from collections.abc import Iterable
from typing import Literal

from dishka import AsyncContainer, Scope

from service_api.application.ports import CacheRepository
from service_api.infrastructure.arq_worker_tasks.config import _dishka_container


async def clear_cache(
    ctx,  # noqa: ARG001
    groups: Iterable[str],
    cabinets: Iterable[str],
    schedule_to: Literal["today", "tomorrow"],
):
    container: AsyncContainer = _dishka_container

    async with container(scope=Scope.REQUEST) as cont:
        cache_repository: CacheRepository = await cont.get(CacheRepository)

        if groups:
            await cache_repository.delete_group_cache(groups)
            await cache_repository.delete_group_day_schedule_cache(schedule_to, groups)

        if cabinets:
            await cache_repository.delete_cabinet_cache(cabinets)
            await cache_repository.delete_cabinet_day_schedule_cache(
                schedule_to, cabinets
            )

    return "Items was removed successfully"
