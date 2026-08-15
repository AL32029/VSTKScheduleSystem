import asyncio
import logging
from pathlib import Path

from watchfiles import Change, awatch
from watchfiles._rust_notify import WatchfilesRustInternalError

from ..database import (
    BaseProdDatabaseSettings,
    DatabaseEngineManager,
)
from ..redis import BaseProdRedisSettings, RedisClientManager

logger = logging.getLogger(__name__)


class WatchFilesManager:
    def __init__(
        self,
        db_settings: "BaseProdDatabaseSettings",
        redis_settings: "BaseProdRedisSettings",
    ):
        self.db_paths = {
            db_settings.SSL_CERT_FILE,
            db_settings.SSL_KEY_FILE,
            db_settings.SSL_CA_CERT_FILE,
        }
        self.redis_paths = {
            redis_settings.SSL_CERT_FILE,
            redis_settings.SSL_KEY_FILE,
            redis_settings.SSL_CA_CERT_FILE,
        }

    async def watch(
        self,
        db_manager: "DatabaseEngineManager",
        redis_client: "RedisClientManager",
    ):
        logger.info("Launching tracking of changes in secrets")

        all_paths = self.db_paths | self.redis_paths

        watch_dirs = {str(Path(p).parent) for p in all_paths}

        def relevant_change(change: Change, path: str) -> bool:  # noqa: ARG001
            return path in all_paths

        try:
            async for changes in awatch(
                *watch_dirs,
                watch_filter=relevant_change,
                debounce=2000,
            ):
                logger.info("Changes have been detected in the tracked secrets")
                certs_changes = {p for _, p in changes}

                tasks_run = []
                if self.db_paths & certs_changes:
                    logger.info("Initialization of database secret rotation")
                    tasks_run.append(asyncio.create_task(db_manager.rotate()))
                if self.redis_paths & certs_changes:
                    logger.info("Initialization of redis secret rotation")
                    tasks_run.append(asyncio.create_task(redis_client.rotate()))

                await asyncio.gather(*tasks_run, return_exceptions=True)
        except (WatchfilesRustInternalError, PermissionError, OSError, RuntimeError):
            logger.exception("Error while tracking changes in secrets")

        logger.info("Tracking of changes in secrets has been discontinued")
