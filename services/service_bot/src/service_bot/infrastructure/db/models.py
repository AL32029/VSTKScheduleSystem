from sqlalchemy import BigInteger, ForeignKey, Index, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserORM(Base):
    """ORM-модель пользователь бота"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(BigInteger, index=True, unique=True)

    user_metadata: Mapped[list["UserMetadataORM"]] = relationship(
        "UserMetadataORM",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    group_subscribes: Mapped[list["GroupSubscribesORM"]] = relationship(
        "GroupSubscribesORM",
        back_populates="user",
        lazy="selectin",
        order_by="GroupSubscribesORM.group_index",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    cabinet_subscribes: Mapped[list["CabinetSubscribesORM"]] = relationship(
        "CabinetSubscribesORM",
        back_populates="user",
        lazy="selectin",
        order_by="CabinetSubscribesORM.cabinet_index",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class UserMetadataORM(Base):
    """ORM-модель метаданных пользователя [One to Many связь с UserORM]"""

    __tablename__ = "user_metadata"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
    )

    key: Mapped[str] = mapped_column(String(96))
    value: Mapped[str | None] = mapped_column(String, nullable=True)

    user: Mapped["UserORM"] = relationship(
        "UserORM", back_populates="user_metadata", lazy="noload",
    )

    __table_args__ = (
        Index("idx_user_metadata_user_id_key", "user_id", "key", unique=True),
    )

    def __hash__(self):
        return hash((self.user_id, self.key))


class GroupSubscribesORM(Base):
    """ORM-модель подписок на группу [One to Many связь с UserORM]"""

    __tablename__ = "group_subscribes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
    )
    group_index: Mapped[str] = mapped_column(String(6))

    user: Mapped["UserORM"] = relationship(
        "UserORM", back_populates="group_subscribes", lazy="noload",
    )

    __table_args__ = (
        Index("idx_group_subscribes_user_id", "user_id", "group_index", unique=True),
    )

    def __hash__(self):
        return hash((self.user_id, self.group_index))


class CabinetSubscribesORM(Base):
    """ORM-модель подписок на кабинет [One to Many связь с UserORM]"""

    __tablename__ = "cabinet_subscribes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
    )
    cabinet_index: Mapped[str] = mapped_column(String(6))

    user: Mapped["UserORM"] = relationship(
        "UserORM", back_populates="cabinet_subscribes", lazy="noload",
    )

    __table_args__ = (
        Index(
            "idx_cabinet_subscribes_user_id", "user_id", "cabinet_index", unique=True,
        ),
    )

    def __hash__(self):
        return hash((self.user_id, self.cabinet_index))
