import asyncio
from typing import cast

from redis.asyncio import Redis

from service_api.infrastructure.config import RedisSettings


class RedisClientManager:
    def __init__(self, settings: 'RedisSettings'):
        print('RedisClientManager initializing...')
        self.settings = settings
        self._client: Redis | None = None
        self._lock = asyncio.Lock()
        print('RedisClientManager initialized')

    async def get_client(self) -> Redis:
        print('Getting Redis client...')
        if self._client is None:
            async with self._lock:
                if self._client is None:
                    print('Redis client is missing, building...')
                    self._client = self._build_client()

        print('Redis client retrieved')
        return cast(Redis, self._client)

    async def rotate(self) -> bool:
        print('Rotating of Redis client is started')
        async with self._lock:
            print('Set old client in old_client var')
            old_client = self._client

            try:
                print('Build new Redis client and set in new_client var')
                new_client = self._build_client()
                print('Ping new Redis client')
                await new_client.ping()
                print('Ping is successfully')
                print('Set new client in self._client var')
                self._client = new_client

                if old_client is not None:
                    print('Start close Redis client task')
                    asyncio.create_task(self._close_client(old_client))

                print('Redis client rotation completed successfully')
                return True
            except Exception as e:
                print(f'Error at building new Redis client: {e!r}')
                print('Redis client rotation failed')
                return False

    async def close(self, delay: float = 15.0) -> None:
        if self._client is not None:
            await self._close_client(self._client, delay)

    def _build_client(self) -> Redis:
        print('Build new Redis client')
        return Redis(
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

    async def _close_client(self, client: Redis, delay: float = 30.0):
        print(f'Close Redis client is started, wait {delay} sec...')
        await asyncio.sleep(delay)
        print('Closing Redis client...')
        await client.aclose()
        print('Redis client was closed')
