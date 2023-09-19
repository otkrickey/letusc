import asyncio

from .logger import L

__all__ = [
    "TaskManager",
]


class TaskManager:
    _l = L()
    _instance: "TaskManager"
    _loop = asyncio.get_event_loop()
    _exit_event = asyncio.Event()

    def __new__(cls) -> "TaskManager":
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__init__")
        _l.info("TaskManager initialized")

    def start(self):
        _l = self._l.gm("start")
        try:
            self._loop.run_forever()
        except KeyboardInterrupt:
            _l.info("KeyboardInterrupt")
        finally:
            self._exit_event.set()
            pending = asyncio.all_tasks(loop=self._loop)
            try:
                self._loop.run_until_complete(asyncio.gather(*pending))
            except asyncio.CancelledError as e:
                _l.info(f"CancelledError: {e}")
            self._loop.close()

    @classmethod
    def get_loop(cls) -> asyncio.AbstractEventLoop:
        _l = L(cls.__name__).gm("get_loop")
        return cls._loop

    @staticmethod
    def get_exit_event() -> asyncio.Event:
        _l = L(TaskManager.__name__).gm("get_exit_event")
        return TaskManager._exit_event
