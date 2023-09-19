from aiohttp import ClientSession
from letusc.TaskManager import TaskManager
from letusc.logger import L


__all__ = [
    "SessionManager",
]


class SessionManager:
    _l = L()
    _session = None

    @classmethod
    def get(cls) -> ClientSession:
        cls._l = L(cls.__name__)
        _l = cls._l.gm("get")
        if cls._session is None:
            _l.info("Creating session")
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
        cls._l = L(cls.__name__)
        _l = cls._l.gm("wait_exit")
        await TaskManager.get_exit_event().wait()
        if cls._session:
            await cls._session.close()
            cls._session = None
        _l.info("session closed")
