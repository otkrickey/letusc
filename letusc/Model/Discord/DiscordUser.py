from dataclasses import dataclass
from typing import Optional, Union

from letusc.logger import Log
from letusc.Model.BaseModel import BaseModel


@dataclass
class DiscordUserBase(BaseModel):
    __logger = Log("Model.DiscordUserBase")
    discord_id: str
    username: Optional[str] = None
    discriminator: Optional[str] = None

    @classmethod
    def from_api(cls, object: dict) -> Union["DiscordUser", "DiscordUserAny"]:
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
        return {"username": self.username, "discriminator": self.discriminator}


@dataclass
class DiscordUserAny(DiscordUserBase):
    __logger = Log("Model.DiscordUserAny")


@dataclass
class DiscordUser(DiscordUserAny):
    __logger = Log("Model.DiscordUser")
    username: str
    discriminator: str
