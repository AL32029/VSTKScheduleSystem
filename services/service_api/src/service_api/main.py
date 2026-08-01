from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from service_api.infrastructure.di.container import get_dishka_container
from service_api.presentation.rest.endpoints import (
    cabinet_router,
    group_router,
    schedule_router,
)


def create_app(container=None) -> FastAPI:
    app = FastAPI(
        title='Schedule API system',
        description='The API is designed to retrieve the schedule of classes at '
                    'Vitebsk State Technical College (Vitebsk, Belarus)'
    )

    setup_dishka(container or get_dishka_container(), app)
    app.include_router(group_router)
    app.include_router(cabinet_router)
    app.include_router(schedule_router)

    return app

