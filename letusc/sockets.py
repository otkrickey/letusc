from dataclasses import asdict
import socketio


from .logger import get_logger
from .models.account import NewAccount
from .models.event import ExtendedLoginEventPayload, Progress, Status
from .util import env

logger = get_logger(__name__)

__all__ = ["SocketIOClient"]


class LetuscNSP(socketio.AsyncClientNamespace):
    async def on_connect(self):
        print("Connected to server")

    async def on_disconnect(self):
        print("Disconnected from server")

    async def on_login(self, source_data: dict):
        data = ExtendedLoginEventPayload.from_api(source_data)
        print("Login response", data)
        from .authenticator import Authenticator

        account = NewAccount.create(
            student_id=data.student_id,
            discord_id=data.discord_id,
            password=data.password,
            username=data.username,
            discriminator=data.discriminator,
        )
        logger.debug("Login via socket")
        await Authenticator(account, data.client).login_via_socket()
        logger.debug("Login via socket done")


class SocketIOClientBase:
    def __init__(self):
        self.host = env("SOCKET_HOST")
        self.path = env("SOCKET_PATH")
        self.sio = socketio.AsyncClient()
        self.is_connected = False

    async def connect(self):
        self.sio.register_namespace(LetuscNSP(self.path))
        await self.sio.connect(self.host)
        self.is_connected = True

    async def wait(self):
        await self.sio.wait()

    async def disconnect(self):
        await self.sio.disconnect()

    async def send_status(self, status: Status):
        if not self.is_connected:
            return
        await self.sio.emit("status", asdict(status), namespace=self.path)

    async def send_progress(self, progress: Progress):
        if not self.is_connected:
            return
        await self.sio.emit("progress", asdict(progress), namespace=self.path)


class SocketIOClient:
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = SocketIOClientBase()
        return cls._instance
