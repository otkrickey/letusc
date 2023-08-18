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
            cls.__logger.error(f"object must have discord_id: {e}")
            raise KeyError("Model.DiscordUserBase.from_api:KeyError")
        else:
            try:
                username = object["Discord"]["username"]
                discriminator = object["Discord"]["discriminator"]
            except KeyError as e:
                cls.__logger.warn(f"object has no key: {e}")
                return DiscordUserAny(discord_id)
            else:
                return DiscordUser(discord_id, username, discriminator)


@dataclass
class DiscordUserAny(DiscordUserBase):
    __logger = Log("Model.DiscordUserAny")


@dataclass
class DiscordUser(DiscordUserAny):
    __logger = Log("Model.DiscordUser")
    username: str
    discriminator: str
