import asyncio
import logging
import ssl
from ssl import SSLContext
from typing import cast

import aiofiles
import asyncpg.exceptions
import sqlalchemy.exc
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from sqlalchemy import URL, text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from service_bot.infrastructure.config import DatabaseSettings

logger = logging.getLogger(__name__)


class DatabaseEngineManager:
    def __init__(self, settings: "DatabaseSettings") -> None:
        logger.info("Initialization of the database manager")
        self.settings = settings
        self._engine: AsyncEngine | None = None
        self._lock = asyncio.Lock()
        logger.info("The database manager has been successfully initialized")

    async def get_engine(self) -> AsyncEngine:
        logger.info("Obtaining the database engine")
        if self._engine is None:
            async with self._lock:
                if self._engine is None:
                    logger.warning("The database engine is missing, creating...")
                    self._engine = await self._build_engine()

        logger.info("The database engine has been obtained")
        return cast(AsyncEngine, self._engine)

    async def rotate(self) -> bool:
        logger.info("The process of rotating database credentials has begun")
        async with self._lock:
            old_engine = self._engine

            try:
                logger.info("Creating a new database engine")
                new_engine = await self._build_engine()

                logger.info(
                    "Checking the correctness of the connection to the database "
                    "via the new engine"
                )
                async with new_engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                logger.info(
                    "The connection to the database via the new engine was successful"
                )

                self._engine = new_engine

                if old_engine is not None:
                    logger.info(
                        "Closing connections to the database via the old engine"
                    )
                    asyncio.create_task(self._dispose_engine(old_engine))

                logger.info(
                    "The database credential rotation process "
                    "was completed successfully"
                )
                return True
            except (sqlalchemy.exc.SQLAlchemyError, asyncpg.exceptions.PostgresError):
                logger.exception(
                    "The database credential rotation process has completed "
                    "with an error"
                )
                return False

    async def dispose(self, delay: float = 15.0) -> None:
        if self._engine is not None:
            await self._dispose_engine(self._engine, delay)

    async def _build_engine(self):
        logger.info("Creating a database engine")
        ssl_context = self._load_ssl_context()
        engine_url = await self._build_engine_url()
        engine = create_async_engine(
            engine_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            connect_args={"ssl": ssl_context},
        )
        logger.info("The database engine has been created")
        return engine

    async def _dispose_engine(self, engine: AsyncEngine, delay: float = 30.0) -> None:
        logger.info(
            "The process of closing database connections is scheduled "
            "to begin in %s seconds",
            delay,
        )
        await asyncio.sleep(delay)
        logger.info("The closing of database connections has begun")
        await engine.dispose()
        logger.info("Database connections are closed")

    def _load_ssl_context(self) -> SSLContext:
        logger.info("Loading the SSL context")
        ssl_context = ssl.create_default_context(cafile=self.settings.SSL_CA_CERT_FILE)
        ssl_context.load_cert_chain(
            certfile=self.settings.SSL_CERT_FILE, keyfile=self.settings.SSL_KEY_FILE
        )
        logger.info("The SSL context has been loaded")
        return ssl_context

    async def _build_engine_url(self) -> URL:
        logger.info("Database connection URL generation")
        async with aiofiles.open(self.settings.SSL_CERT_FILE, "rb") as f:
            cert_data = await f.read()

        cert = x509.load_pem_x509_certificate(cert_data, default_backend())

        common_name = str(
            cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
        )

        url = URL.create(
            "postgresql+asyncpg",
            username=common_name,
            host=self.settings.HOST,
            port=self.settings.PORT,
            database=self.settings.BASE,
        )
        logger.info("The database connection URL has been generated")
        return url
