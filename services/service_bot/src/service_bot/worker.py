import logging.config

from dishka.integrations.arq import setup_dishka

from service_bot.infrastructure.arq_worker_tasks import notify_users
from service_bot.infrastructure.arq_worker_tasks.config import (
    _dishka_container,
    _redis_manager,
)
from service_bot.infrastructure.config import LoggingSettings

logging.config.dictConfig(LoggingSettings().model_dump(mode="json"))


class WorkerSettings:
    functions = [notify_users]
    redis_settings = _redis_manager.arq_settings
    queue_name = "notifications"

    max_jobs = 20
    job_timeout = 600
    keep_result = 3600


setup_dishka(container=_dishka_container, worker_settings=WorkerSettings)
