from dataclasses import asdict, dataclass, field
from enum import Enum, auto

from ..logger import get_logger

logger = get_logger(__name__)

__all__ = [
    "LoginEventPayload",
    "ExtendedLoginEventPayload",
    "StatusPayload",
    "Progress",
]


@dataclass
class LoginEventPayload:
    student_id: str
    discord_id: str
    password: str
    username: str
    discriminator: str


@dataclass
class ExtendedLoginEventPayload(LoginEventPayload):
    client: str

    @classmethod
    def from_api(cls, object: dict) -> "ExtendedLoginEventPayload":
        try:
            student_id = object["student_id"]
            discord_id = object["discord_id"]
            password = object["password"]
            username = object["username"]
            discriminator = object["discriminator"]
            client = object["client"]
        except KeyError as e:
            raise KeyError("Model.ExtendedLoginEventPayload.from_api:KeyError") from e
        else:
            return cls(
                student_id=student_id,
                discord_id=discord_id,
                password=password,
                username=username,
                discriminator=discriminator,
                client=client,
            )


@dataclass
class StatusPayload:
    connected: bool
    alive: bool


class Status(Enum):
    START = "start"
    SUCCESS = "success"
    WAIT = "wait"
    CLICK = "click"
    INPUT = "input"
    END = "end"
    ERROR = "error"


@dataclass
class Progress:
    client: str
    type: str
    message: str
    status: Status
    progress: int
    total: int = field(init=False, default=22)
