import asyncio
import ssl
from ssl import SSLContext
from typing import cast

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from sqlalchemy import URL, text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from service_api.infrastructure.config import DatabaseSettings


class DatabaseEngineManager:
    def __init__(self, settings: 'DatabaseSettings') -> None:
        print('DatabaseEngineManager initializing...')
        self.settings = settings
        self._engine: AsyncEngine | None = None
        self._lock = asyncio.Lock()
        print('DatabaseEngineManager initialized')

    async def get_engine(self) -> 'AsyncEngine':
        print('Getting database engine...')
        if self._engine is None:
            async with self._lock:
                if self._engine is None:
                    print('Database engine is missing, building...')
                    self._engine = self._build_engine()

        print('Database engine retrieved')
        return cast('AsyncEngine', self._engine)

    async def rotate(self) -> bool:
        print('Rotating of database engine is started')
        async with self._lock:
            print('Set old engine in old_engine var')
            old_engine = self._engine

            try:
                print('Build new database engine and set in new_engine var')
                new_engine = self._build_engine()

                print('Check new database engine connection with SELECT 1')
                async with new_engine.connect() as conn:
                    await conn.execute(text('SELECT 1'))
                print('Connection check successful')

                print('Set new engine in self._engine var')
                self._engine = new_engine

                if old_engine is not None:
                    print('Start dispose old engine task')
                    asyncio.create_task(self._dispose_engine(old_engine))

                print('Database engine rotation completed successfully')
                return True
            except Exception as e:
                print(f'Error at building new database engine: {e!r}')
                print('Database engine rotation failed')
                return False

    async def dispose(self, delay: float = 15.0) -> None:
        if self._engine is not None:
            await self._dispose_engine(self._engine, delay)

    def _build_engine(self):
        print('Building new database engine...')
        ssl_context = self._load_ssl_context()
        engine_url = self._build_engine_url()
        engine = create_async_engine(
            engine_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            connect_args={'ssl': ssl_context}
        )
        print('New database engine built')
        return engine

    async def _dispose_engine(self, engine: 'AsyncEngine', delay: float = 30.0) -> None:
        print(f'Disposing old database engine, wait {delay} sec...')
        await asyncio.sleep(delay)
        print('Disposing database engine...')
        await engine.dispose()
        print('Database engine disposed')

    def _load_ssl_context(self) -> 'SSLContext':
        print('Loading SSL context...')
        ssl_context = ssl.create_default_context(cafile=self.settings.SSL_CA_CERT_FILE)
        ssl_context.load_cert_chain(
            certfile=self.settings.SSL_CERT_FILE,
            keyfile=self.settings.SSL_KEY_FILE
        )
        print('SSL context loaded')
        return ssl_context

    def _build_engine_url(self) -> 'URL':
        print('Building engine URL...')
        with open(self.settings.SSL_CERT_FILE, 'rb') as f:
            cert_data = f.read()

        cert = x509.load_pem_x509_certificate(cert_data, default_backend())

        common_name = str(cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value)

        url = URL.create(
            'postgresql+asyncpg',
            username=common_name,
            host=self.settings.HOST,
            port=self.settings.PORT,
            database=self.settings.BASE
        )
        print('Engine URL built')
        return url
