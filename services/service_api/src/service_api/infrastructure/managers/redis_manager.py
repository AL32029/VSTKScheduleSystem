import asyncio
import logging
from typing import cast

from redis import RedisError
from redis.asyncio import Redis

from service_api.infrastructure.config import RedisSettings

logger = logging.getLogger(__name__)

class RedisClientManager:
    def __init__(self, settings: 'RedisSettings'):
        logger.info('Initialization of the redis manager has begun')
        self.settings = settings
        self._client: Redis | None = None
        self._lock = asyncio.Lock()
        logger.info('The redis manager has been successfully initialized')

    async def get_client(self) -> Redis:
        logger.info('Obtaining the redis client')
        if self._client is None:
            async with self._lock:
                if self._client is None:
                    logger.warning('The redis client is missing; create a new client')
                    self._client = self._build_client()

        logger.info('The redis client has been obtained')
        return cast(Redis, self._client)

    async def rotate(self) -> bool:
        logger.info('The rotation of redis secrets has begun')
        async with self._lock:
            old_client = self._client
            try:
                logger.info('Initialization of the new redis client assembly')
                new_client = self._build_client()
                logger.info('The assembly of the new redis client has been successfully completed')
                
                logger.info('Checking the redis connection status via the new client')
                await new_client.ping()
                logger.info('The check of the redis connection status via the new client was successful')
                
                self._client = new_client

                if old_client is not None:
                    logger.info('Adding a task to disconnect connections to the redis via the old client')
                    asyncio.create_task(self._close_client(old_client))
                    logger.info('The task to disconnect from the redis via the old '
                                'client has been successfully added')

                logger.info('The redis secret rotation has been completed successfully')
                return True
            except (RedisError, TimeoutError, ConnectionError):
                logger.exception('An error occurred during the rotation of redis secrets')
                return False

    async def close(self, delay: float = 15.0) -> None:
        if self._client is not None:
            await self._close_client(self._client, delay)

    def _build_client(self) -> Redis:
        logger.info('The redis client has begun to be assembled')
        client = Redis(
            host=self.settings.HOST,
            port=self.settings.PORT,
            db=self.settings.DB_NUMBER,
            ssl=True,
            ssl_certfile=self.settings.SSL_CERT_FILE,
            ssl_keyfile=self.settings.SSL_KEY_FILE,
            ssl_ca_certs=self.settings.SSL_CA_CERT_FILE,
            ssl_cert_reqs=self.settings.SSL_CERT_REQS,
            ssl_check_hostname=self.settings.SSL_CHECK_HOSTNAME
        )
        logger.info('The redis client has been successfully created')
        return client

    async def _close_client(self, client: Redis, delay: float = 30.0):
        logger.info('The connections through the old redis client will be terminated in %s seconds', delay)
        await asyncio.sleep(delay)
        logger.info('Disruption of connections via the old redis client')
        await client.aclose()
        logger.info('Connections through the old redis client have been successfully terminated')
