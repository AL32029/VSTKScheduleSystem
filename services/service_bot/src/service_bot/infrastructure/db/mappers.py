import json

from service_bot.domain.entities import User

from .models import (
    CabinetSubscribesORM,
    GroupSubscribesORM,
    UserMetadataORM,
    UserORM,
)


def user_domain_to_orm(user: "User") -> "UserORM":
    """Преобразование доменной сущности User в ORM-модель UserORM"""
    return UserORM(
        user_id=user.user_id,
        user_metadata=list(
            {
                UserMetadataORM(
                    user_id=user.user_id, key=k, value=json.dumps(v, ensure_ascii=False)
                )
                for k, v in user.metadata.items()
            }
        ),
        group_subscribes=list(
            {
                GroupSubscribesORM(user_id=user.user_id, group_index=group)
                for group in user.group_subscribes
            }
        ),
        cabinet_subscribes=list(
            {
                CabinetSubscribesORM(user_id=user.user_id, cabinet_index=cabinet)
                for cabinet in user.cabinet_subscribes
            }
        ),
    )


def user_orm_to_domain(user_orm: "UserORM") -> "User":
    """Преобразование ORM-модели UserORM в доменную сущность User"""
    return User(
        user_id=user_orm.user_id,
        metadata={
            metadata.key: json.loads(metadata.value)
            if metadata.value is not None
            else None
            for metadata in user_orm.user_metadata
        },
        group_subscribes=sorted(
            [group.group_index for group in user_orm.group_subscribes], key=lambda x: x
        ),
        cabinet_subscribes=sorted(
            [cabinet.cabinet_index for cabinet in user_orm.cabinet_subscribes],
            key=lambda x: x,
        ),
    )
