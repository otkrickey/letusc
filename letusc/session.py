from aiohttp import ClientSession

from .logger import get_logger
from .task import TaskManager

logger = get_logger(__name__)

__all__ = [
    "SessionManager",
]


class SessionManager:
    _session = None

    @classmethod
    def get(cls) -> ClientSession:
        if cls._session is None:
            logger.info("Creating session")
            cls._session = ClientSession()
            TaskManager.get_loop().create_task(cls.wait_exit())
        cls._session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
            }
        )
        return cls._session

    @classmethod
    async def wait_exit(cls):
        await TaskManager.get_exit_event().wait()
        if cls._session:
            await cls._session.close()
            cls._session = None
        logger.info("session closed")
