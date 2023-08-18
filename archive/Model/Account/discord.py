from dataclasses import dataclass, field
from typing import Optional, Union

from letusc.logger import Log


@dataclass
class DiscordUser:
    __logger = Log("Model.DiscordUser")
    # [must]
    user_id: str
    # [api]
    username: Optional[str] = None
    discriminator: Optional[str] = None

    @classmethod
    def from_api(cls, account: dict) -> Union["DiscordUser", "DiscordUserFull"]:
        try:
            user_id = account["discord_id"]
            username = account["Discord"]["username"]
            discriminator = account["Discord"]["discriminator"]
        except KeyError as e:
            cls.__logger.warn(f"account has no key: {e}")
            try:
                user_id = account["discord_id"]
            except KeyError as e:
                cls.__logger.error(f"account must have discord_id: {e}")
                raise KeyError("Model.DiscordUser.from_api:KeyError")
            else:
                return cls(user_id)
        else:
            if username and discriminator:
                return DiscordUserFull(user_id, username, discriminator)
            else:
                return cls(user_id)

    def to_api(self) -> dict:
        return {"username": self.username, "discriminator": self.discriminator}


@dataclass
class DiscordUserFull(DiscordUser):
    __logger = Log("Model.DiscordUserFull")
    username: str
    discriminator: str


@dataclass
class DiscordMessage:
    __logger = Log("Model.DiscordMessage")
    # [must]
    code: str  # the code which includes user_id, guild_id, channel_id, content_id
    # [auto]
    user_id: str = field(init=False)
    guild_id: str = field(init=False)
    channel_id: str = field(init=False)
    content_id: str = field(init=False)
    # [object]
    Discord: DiscordUser = field(init=False)

    def __post_init__(self):
        if len(self.code) != 4:
            self.__logger.error("Invalid code length")
            raise ValueError("Model.DiscordMessage:CodeError")
        self.user_id = self.code[0]
        self.guild_id = self.code[1]
        self.channel_id = self.code[2]
        self.content_id = self.code[3]
        self.Discord = DiscordUser(self.user_id)
