from dataclasses import dataclass

from ..logger import L
from .base import BaseModel, attrs, to_api_attrs, types

__all__ = [
    "DiscordUserBase",
    "DiscordUserAny",
    "DiscordUser",
]


@dataclass
class DiscordUserBase(BaseModel):
    _l = L()
    _attrs = BaseModel._attrs | attrs(["discord_id", "username", "discriminator"])
    _types = BaseModel._types | types(
        [
            ("discord_id", "Discord ID", str),
            ("username", "Discord Username", str),
            ("discriminator", "Discord Discriminator", str),
        ]
    )
    _to_api_attrs = BaseModel._to_api_attrs | to_api_attrs(
        [
            ("username", lambda self: self.username),
            ("discriminator", lambda self: self.discriminator),
        ]
    )

    discord_id: str

    username: str | None = None
    discriminator: str | None = None

    def __post_init__(self):
        BaseModel.__post_init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")
        self.key_name = "discord_id"
        self.key = self.discord_id

    @classmethod
    def from_api(cls, object: dict) -> "DiscordUserBase":
        try:
            discord_id = object["discord_id"]
        except KeyError as e:
            raise KeyError("Model.DiscordUserBase.from_api:KeyError") from e
        else:
            try:
                username = object["Discord"]["username"]
                discriminator = object["Discord"]["discriminator"]
            except KeyError as e:
                return DiscordUserAny(discord_id)
            else:
                return DiscordUser(discord_id, username, discriminator)


@dataclass
class DiscordUserAny(DiscordUserBase):
    _l = L()
    _types = DiscordUserBase._types | types([("discord_id", "Discord ID", str)])

    def __post_init__(self):
        DiscordUserBase.__post_init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")


@dataclass
class DiscordUser(DiscordUserAny):
    _l = L()
    _types = DiscordUserAny._types | types(
        [
            ("discord_id", "Discord ID", str),
            ("username", "Discord Username", str),
            ("discriminator", "Discord Discriminator", str),
        ]
    )

    username: str
    discriminator: str

    def __post_init__(self):
        DiscordUserAny.__post_init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")
