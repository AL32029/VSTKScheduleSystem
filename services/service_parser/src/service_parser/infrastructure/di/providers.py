import logging
import ssl
from collections.abc import AsyncGenerator, AsyncIterable
from typing import Any
from zoneinfo import ZoneInfo

import httpx
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from dishka import Provider, Scope, provide
from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from service_parser.application.ports import (
    CabinetRepository,
    GroupRepository,
    ScheduleRepository,
)
from service_parser.infrastructure.config import (
    BaseSystemSettings,
    DatabaseSettings,
    RedisSettings,
)
from service_parser.infrastructure.repositories import (
    SQLAlchemyCabinetRepository,
    SQLAlchemyGroupRepository,
    SQLAlchemyScheduleRepository,
)

logger = logging.getLogger(__name__)


class SystemProvider(Provider):
    scope = Scope.APP

    @provide
    def time_zone(self, base_settings: "BaseSystemSettings") -> ZoneInfo:
        return base_settings.TZ


class DatabaseProvider(Provider):
    scope = Scope.APP

    @provide
    def provide_engine(self) -> "AsyncEngine":
        logger.debug("Creating database engine")
        settings = DatabaseSettings()

        with open(settings.SSL_CERT_FILE, "rb") as f:
            cert_data = f.read()

        cert = x509.load_pem_x509_certificate(cert_data, default_backend())

        common_name = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[
            0
        ].value

        ssl_context = ssl.create_default_context(cafile=settings.SSL_CA_CERT_FILE)
        ssl_context.load_cert_chain(
            certfile=settings.SSL_CERT_FILE, keyfile=settings.SSL_KEY_FILE
        )
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        ssl_context.check_hostname = True

        connection_url = URL.create(
            "postgresql+asyncpg",
            username=str(common_name),
            host=settings.HOST,
            port=settings.PORT,
            database=settings.BASE,
        )

        logger.debug(
            "Database engine created for %s@%s:%s/%s",
            common_name,
            settings.HOST,
            settings.PORT,
            settings.BASE,
        )
        return create_async_engine(
            connection_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            connect_args={"ssl": ssl_context},
        )

    @provide
    def provide_session_maker(
        self, engine: "AsyncEngine"
    ) -> async_sessionmaker["AsyncSession"]:
        logger.debug("Creating session maker")
        return async_sessionmaker(
            bind=engine,
            expire_on_commit=False,
            class_=AsyncSession,
            autoflush=False,
        )

    @provide
    async def provide_session(
        self, session_maker: async_sessionmaker["AsyncSession"]
    ) -> AsyncIterable["AsyncSession"]:
        logger.debug("Creating database session")
        async with session_maker() as session:
            yield session


class RedisProvider(Provider):
    scope = Scope.APP

    @provide
    async def redis_engine(self) -> AsyncIterable["Redis"]:
        settings = RedisSettings()
        logger.debug(
            "Connecting to Redis at %s:%s (db=%s)",
            settings.HOST,
            settings.PORT,
            settings.DB_NUMBER,
        )

        client = Redis(
            host=settings.HOST,
            port=settings.PORT,
            db=settings.DB_NUMBER,
            ssl=True,
            ssl_certfile=settings.SSL_CERT_FILE,
            ssl_keyfile=settings.SSL_KEY_FILE,
            ssl_ca_certs=settings.SSL_CA_CERT_FILE,
            ssl_cert_reqs=settings.SSL_CERT_REQS,
            ssl_check_hostname=settings.SSL_CHECK_HOSTNAME,
        )
        logger.debug("Redis client created")
        yield client
        logger.debug("Closing Redis connection")
        await client.aclose()


class RepositoriesProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def sqlalchemy_cabinet_repository(
        self, session: "AsyncSession"
    ) -> "CabinetRepository":
        return SQLAlchemyCabinetRepository(session)

    @provide
    async def sqlalchemy_group_repository(
        self, session: "AsyncSession"
    ) -> "GroupRepository":
        return SQLAlchemyGroupRepository(session)

    @provide
    async def sqlalchemy_schedule_repository(
        self, session: "AsyncSession"
    ) -> "ScheduleRepository":
        return SQLAlchemyScheduleRepository(session)


class HTTPXClientProvider(Provider):
    scope = Scope.APP

    @provide
    async def provide_client(self) -> AsyncGenerator["AsyncClient", Any]:
        logger.debug("Creating HTTPX client")
        async with httpx.AsyncClient() as client:
            yield client
