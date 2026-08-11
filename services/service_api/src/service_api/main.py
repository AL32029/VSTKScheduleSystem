import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from watchfiles import Change, awatch

from service_api.domain.exceptions import APIServiceException
from service_api.infrastructure.di.container import get_dishka_container
from service_api.infrastructure.managers import (
    DatabaseEngineManager,
    RedisClientManager,
)
from service_api.presentation.rest.endpoints import (
    cabinet_router,
    group_router,
    schedule_router,
)
from service_api.presentation.rest.exception_responses import (
    api_exception_handler,
)


async def watch_loop(db_manager: 'DatabaseEngineManager', redis_client: 'RedisClientManager'):
    print('Watch loop initialized')

    db_paths = {db_manager.settings.SSL_CERT_FILE, db_manager.settings.SSL_KEY_FILE,
                db_manager.settings.SSL_CA_CERT_FILE}
    redis_paths = {redis_client.settings.SSL_CERT_FILE, redis_client.settings.SSL_KEY_FILE,
                   redis_client.settings.SSL_CA_CERT_FILE}
    all_paths = db_paths | redis_paths

    watch_dirs = {str(Path(p).parent) for p in all_paths}

    def relevant_change(change: Change, path: str) -> bool:
        return path in all_paths

    try:
        async for changes in awatch(*watch_dirs, watch_filter=relevant_change, debounce=2000):
            print('New changes view: ', changes)
            certs_changes = {p for _, p in changes}

            tasks_run = []
            if db_paths & certs_changes:
                print('Rotate db engine')
                tasks_run.append(asyncio.create_task(db_manager.rotate()))
            if redis_paths & certs_changes:
                print('Rotate redis client')
                tasks_run.append(asyncio.create_task(redis_client.rotate()))

            await asyncio.gather(*tasks_run, return_exceptions=True)
    except Exception as e:
        print(f"Error in watch_loop: {e}")

    print('Watch loop end')


@asynccontextmanager
async def lifespan(app: 'FastAPI'):
    container = app.state.dishka_container
    db_manager = await container.get(DatabaseEngineManager)
    redis_client = await container.get(RedisClientManager)

    await db_manager.get_engine()
    await redis_client.get_client()

    task = asyncio.create_task(watch_loop(db_manager, redis_client))

    yield

    task.cancel()
    await asyncio.gather(
        db_manager.dispose(),
        redis_client.close(),
        return_exceptions=True,
    )


def create_app(container=None) -> 'FastAPI':
    app = FastAPI(
        title='Schedule API system',
        description='The API is designed to retrieve the schedule of classes at '
                    'Vitebsk State Technical College (Vitebsk, Belarus)',
        lifespan=lifespan,
    )

    setup_dishka(container or get_dishka_container(), app)

    app.include_router(cabinet_router)
    app.include_router(group_router)
    app.include_router(schedule_router)

    app.add_exception_handler(APIServiceException, api_exception_handler)

    return app