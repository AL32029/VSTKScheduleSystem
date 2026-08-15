from .cabinet_endpoints import cabinet_router
from .group_endpoints import group_router
from .schedule_endpoints import schedule_router

__all__ = [
    'cabinet_router',
    'group_router',
    'schedule_router'
]
