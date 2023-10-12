import asyncio

from .logger import get_logger

logger = get_logger(__name__)

__all__ = [
    "TaskManager",
]


class TaskManager:
    _instance: "TaskManager"
    _loop = asyncio.get_event_loop()
    _exit_event = asyncio.Event()

    def __new__(cls) -> "TaskManager":
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        logger.info("TaskManager initialized")

    def start(self):
        try:
            self._loop.run_forever()
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt")
        finally:
            self._exit_event.set()
            pending = asyncio.all_tasks(loop=self._loop)
            try:
                self._loop.run_until_complete(asyncio.gather(*pending))
            except asyncio.CancelledError as e:
                logger.info(f"CancelledError: {e}")
            self._loop.close()

    @classmethod
    def get_loop(cls) -> asyncio.AbstractEventLoop:
        return cls._loop

    @staticmethod
    def get_exit_event() -> asyncio.Event:
        return TaskManager._exit_event
