import asyncio
import logging
import logging.config
from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from prometheus_client import make_asgi_app
from system_managers import (
    DatabaseEngineManager,
    RedisClientManager,
    WatchFilesManager,
)

from service_api.domain.exceptions import APIServiceError
from service_api.infrastructure.config import LoggingSettings, SystemSettings
from service_api.infrastructure.di.container import get_dishka_container
from service_api.infrastructure.middlewares import InitRequestMiddleware
from service_api.presentation.rest.endpoints import (
    cabinet_router,
    group_router,
    schedule_router,
)
from service_api.presentation.rest.exception_responses import (
    api_exception_handler,
)

logging.config.dictConfig(LoggingSettings().model_dump(mode="json"))

logger = logging.getLogger("service_api")


@asynccontextmanager
async def lifespan(app: "FastAPI"):  # noqa: C901
    container = app.state.dishka_container

    system_settings: SystemSettings = await container.get(SystemSettings)
    logger.info("Starting application in %s mode", system_settings.SYSTEM_MODE)

    watch_files_task: asyncio.Task | None = None

    db_manager: DatabaseEngineManager = await container.get(DatabaseEngineManager)
    redis_client: RedisClientManager = await container.get(RedisClientManager)

    await db_manager.rotate()
    await redis_client.rotate()

    if system_settings.SYSTEM_MODE == "prod":
        watch_files_manager: WatchFilesManager = await container.get(WatchFilesManager)

        try:
            watch_files_task = asyncio.create_task(
                watch_files_manager.watch(db_manager, redis_client)
            )
            logger.info("Watchfiles task started")
        except Exception:
            logger.exception("Failed to start watchfiles task")

    yield

    if system_settings.SYSTEM_MODE == "prod":
        if watch_files_task and not watch_files_task.done():
            watch_files_task.cancel()
            try:
                await watch_files_task
            except asyncio.CancelledError:
                logger.info("Watchfiles task cancelled")
            except Exception:
                logger.exception("Watchfiles task failed during shutdown")

        if db_manager is not None:
            try:
                await db_manager.dispose()
            except Exception:
                logger.exception("Error disposing database engine")

        if redis_client is not None:
            try:
                await redis_client.close()
            except Exception:
                logger.exception("Error closing Redis client")

    logger.info("Application shutdown complete")


def create_app(container=None) -> "FastAPI":
    app = FastAPI(
        title="Schedule API system",
        description="The API is designed to retrieve the schedule of classes at "
        "Vitebsk State Technical College (Vitebsk, Belarus)",
        lifespan=lifespan,
    )

    setup_container = container or get_dishka_container()

    setup_dishka(setup_container, app)

    app.include_router(cabinet_router)
    app.include_router(group_router)
    app.include_router(schedule_router)

    app.add_exception_handler(APIServiceError, api_exception_handler)

    app.add_middleware(InitRequestMiddleware)

    app.mount("/metrics", make_asgi_app())

    return app
