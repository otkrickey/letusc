from dataclasses import dataclass

from letusc.logger import Log
from letusc.Model.Discord import DiscordUser
from letusc.Model.Letus import LetusUser

from .AccountBase import AccountBase
from .Database import Database


@dataclass
class Account(Database, AccountBase):
    __logger = Log("Model.Account")

    def __post_init__(self):
        account = self.pull()
        self.student_id = account["student_id"]
        self.discord_id = account["discord_id"]
        self.Letus = LetusUser.from_api(account)
        self.Discord = DiscordUser.from_api(account)


__all__ = [
    "Account",
]
