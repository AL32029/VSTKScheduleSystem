from collections.abc import Iterable
from datetime import date
from typing import Literal

from arq import ArqRedis

from service_parser.application.ports import TasksRepository
from service_parser.domain.entities import Cabinet, Group


class ARQTasksRepository(TasksRepository):
    def __init__(self, client: "ArqRedis"):
        self.client = client

    async def send_clear_cache_task(
        self,
        groups: Iterable[str],
        cabinets: Iterable[str],
        schedule_to: Literal["today", "tomorrow"],
    ):
        await self.client.enqueue_job(
            "clear_cache",
            groups=groups,
            cabinets=cabinets,
            schedule_to=schedule_to,
            _queue_name="cache",
        )

    async def send_notify_task(
        self,
        changes: dict[
            date,
            dict[
                Literal["group", "cabinet"],
                dict[Literal["new", "update", "remove"], set["Group | Cabinet"]],
            ],
        ],
    ):
        await self.client.enqueue_job(
            "notify_users",
            changes=changes,
            _queue_name="notifications",
        )
