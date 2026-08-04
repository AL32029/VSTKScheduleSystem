import datetime
from typing import Iterable

from sqlalchemy import String, Integer, Date, Time, ForeignKey, BigInteger, SmallInteger, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class GroupORM(Base):
    __tablename__ = 'groups'

    index: Mapped[str] = mapped_column(String(6), primary_key=True, index=True)
    number: Mapped[str] = mapped_column(String(7))

    lesson_relationships: Mapped[list['LessonORM']] = relationship(
        'LessonORM',
        back_populates='group',
        lazy='noload',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    def __str__(self):
        return self.number


class CabinetORM(Base):
    __tablename__ = 'cabinets'

    index: Mapped[str] = mapped_column(String(32), primary_key=True, index=True)
    number: Mapped[str] = mapped_column(String(48))

    cabinet_relationships: Mapped[list['LessonCabinetORM']] = relationship(
        'LessonCabinetORM',
        back_populates='cabinet_item',
        lazy='selectin'
    )

    redirects_from: Mapped[list['CabinetRedirectORM']] = relationship(
        'CabinetRedirectORM',
        back_populates='to_cab',
        foreign_keys='[CabinetRedirectORM.to_id]',
        lazy='noload',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    redirect_to: Mapped['CabinetRedirectORM'] = relationship(
        'CabinetRedirectORM',
        back_populates='from_cab',
        foreign_keys='[CabinetRedirectORM.from_id]',
        lazy='joined'
    )

    @property
    def redirected(self) -> 'CabinetORM':
        if not self.redirect_to:
            return self

        return self.redirect_to.to_cab

    def __str__(self) -> str:
        return self.number


class CabinetRedirectORM(Base):
    __tablename__ = 'cabinet_redirects'

    from_id: Mapped[str] = mapped_column(ForeignKey('cabinets.index', ondelete='CASCADE'), primary_key=True, index=True)
    to_id: Mapped[str] = mapped_column(ForeignKey('cabinets.index', ondelete='CASCADE'), index=True)

    from_cab: Mapped['CabinetORM'] = relationship(
        'CabinetORM',
        back_populates='redirect_to',
        foreign_keys='[CabinetRedirectORM.from_id]',
        lazy='joined'
    )
    to_cab: Mapped['CabinetORM'] = relationship(
        'CabinetORM',
        back_populates='redirects_from',
        foreign_keys='[CabinetRedirectORM.to_id]',
        lazy='noload'
    )


class LessonORM(Base):
    __tablename__ = 'lessons'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    group_index: Mapped[str] = mapped_column(ForeignKey('groups.index', ondelete='CASCADE'))

    date: Mapped[datetime.date] = mapped_column(Date, index=True)
    start: Mapped[datetime.time] = mapped_column(Time)
    end: Mapped[datetime.time] = mapped_column(Time)

    name: Mapped[str] = mapped_column(String)

    cabinet_relationships: Mapped[list['LessonCabinetORM']] = relationship(
        'LessonCabinetORM',
        back_populates='lesson_item',
        lazy='selectin',
        cascade='all, delete-orphan',
        passive_deletes=True,
        order_by='LessonCabinetORM.cabinet_index'
    )
    group: Mapped['GroupORM'] = relationship(
        'GroupORM',
        back_populates='lesson_relationships',
        lazy='joined'
    )

    __table_args__ = (
        Index('idx_lessons_group_index_date', 'group_index', 'date', unique=False),
    )

    @property
    def cabinets_without_redirects(self) -> list['CabinetORM']:
        return [cabinet.cabinet_item
                for cabinet in self.cabinet_relationships]

    @property
    def cabinets_with_redirects(self) -> list['CabinetORM']:
        return [cabinet.cabinet_item.redirected
                for cabinet in self.cabinet_relationships]


class LessonCabinetORM(Base):
    __tablename__ = 'lessons_cabinets'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    lesson_id: Mapped[int] = mapped_column(ForeignKey('lessons.id', ondelete='CASCADE'))
    cabinet_id: Mapped[str] = mapped_column(ForeignKey('cabinets.index', ondelete='RESTRICT'), index=True)

    cabinet_index: Mapped[int] = mapped_column(SmallInteger)

    lesson_item: Mapped['LessonORM'] = relationship(
        'LessonORM',
        back_populates='cabinet_relationships',
        lazy='joined',
    )
    cabinet_item: Mapped['CabinetORM'] = relationship(
        'CabinetORM',
        back_populates='cabinet_relationships',
        lazy='joined'
    )
