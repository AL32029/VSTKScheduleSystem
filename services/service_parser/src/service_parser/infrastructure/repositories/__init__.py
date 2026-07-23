from .sqlalchemy_group_repo import SQLAlchemyGroupRepository
from .sqlalchemy_cabinet_repo import SQLAlchemyCabinetRepository
from .sqlalchemy_schedule_repo import SQLAlchemyScheduleRepository

# [MISC][DONE] Добавить репозиторий для работы с SQLAlchemy
__all__ = [
    'SQLAlchemyGroupRepository', 'SQLAlchemyScheduleRepository', 'SQLAlchemyCabinetRepository'
]