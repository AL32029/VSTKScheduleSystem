import asyncio
import logging
from typing import cast

import redis.exceptions
from redis.asyncio import Redis

from service_bot.infrastructure.config import RedisSettings

logger = logging.getLogger(__name__)


class RedisClientManager:
    def __init__(self, settings: "RedisSettings"):
        logger.info("Initialization of the redis manager")
        self.settings = settings
        self._client: Redis | None = None
        self._lock = asyncio.Lock()
        logger.info("The redis manager has been successfully initialized")

    async def get_client(self) -> Redis:
        logger.info("Obtaining the redis client")
        if self._client is None:
            async with self._lock:
                if self._client is None:
                    logger.warning("The redis client is missing, creating...")
                    self._client = self._build_client()

        logger.info("The redis client has been obtained")
        return cast(Redis, self._client)

    async def rotate(self) -> bool:
        logger.info("The process of rotating redis credentials has begun")
        async with self._lock:
            old_client = self._client

            try:
                logger.info("Creating a new redis client")
                new_client = self._build_client()

                logger.info(
                    "Checking the correctness of the connection to the redis "
                    "via the new engine"
                )
                await new_client.ping()
                logger.info(
                    "The connection to the redis via the new engine was successful"
                )

                self._client = new_client

                if old_client is not None:
                    logger.info("Closing connections to the redis via the old engine")
                    asyncio.create_task(self._close_client(old_client))

                logger.info(
                    "The redis credential rotation process was completed successfully"
                )
                return True
            except redis.exceptions.RedisError:
                logger.exception(
                    "The redis credential rotation process has completed with an error"
                )
                return False

    async def close(self, delay: float = 15.0) -> None:
        if self._client is not None:
            await self._close_client(self._client, delay)

    def _build_client(self) -> Redis:
        logger.info("Creating a redis client")
        client = Redis(
            host=self.settings.HOST,
            port=self.settings.PORT,
            db=self.settings.DB_NUMBER,
            ssl=True,
            ssl_certfile=self.settings.SSL_CERT_FILE,
            ssl_keyfile=self.settings.SSL_KEY_FILE,
            ssl_ca_certs=self.settings.SSL_CA_CERT_FILE,
            ssl_cert_reqs=self.settings.SSL_CERT_REQS,
            ssl_check_hostname=self.settings.SSL_CHECK_HOSTNAME,
        )
        logger.info("The redis client has been created")
        return client

    async def _close_client(self, client: Redis, delay: float = 30.0):
        logger.info(
            "The process of closing redis connections is scheduled "
            "to begin in %s seconds",
            delay,
        )
        await asyncio.sleep(delay)
        logger.info("The closing of redis connections has begun")
        await client.aclose()
        logger.info("Redis connections are closed")
