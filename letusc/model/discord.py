from dataclasses import dataclass

from letusc.logger import Log

from .base import BaseModel


@dataclass
class DiscordUserBase(BaseModel):
    _logger = Log("Model.DiscordUserBase")
    discord_id: str

    username: str | None = None
    discriminator: str | None = None

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

    def to_api(self) -> dict:
        return {
            "username": self.username,
            "discriminator": self.discriminator,
        }


@dataclass
class DiscordUserAny(DiscordUserBase):
    _logger = Log("Model.DiscordUserAny")


@dataclass
class DiscordUser(DiscordUserAny):
    _logger = Log("Model.DiscordUser")
    username: str
    discriminator: str


__all__ = [
    "DiscordUserBase",
    "DiscordUserAny",
    "DiscordUser",
]
