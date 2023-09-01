from dataclasses import dataclass

import letusc.model.discord as Discord
import letusc.model.letus as Letus
from letusc.logger import Log
from letusc.model.account import Account
from letusc.SessionManager import SessionManager

from .base_task import BaseTask


@dataclass
class AccountTask(BaseTask):
    __logger = Log("Task.AccountTask")
    # [must]
    task: str

    def __post_init__(self):
        pass

    @classmethod
    def from_api(cls, task: dict) -> "AccountTask":
        account = Account(task["discord_id"])

        action = task["task"].split(":")[1]
        match action:
            case "login" | "register":
                return Login.from_copy(account)
            case "status":
                return Status.from_copy(account)
            case _:
                raise KeyError(f"{AccountTask.__logger}.from_api:UnknownAction")


@dataclass
class Login(AccountTask):
    __logger = Log("Task.AccountTask.Login")
    # [auto]
    student_id: str
    discord_id: str
    # [object]
    Discord: Discord.DiscordUser
    Letus: Letus.LetusUserWithPassword

    @classmethod
    def from_copy(cls, account: Account):
        if not isinstance(account.Letus, Letus.LetusUserWithPassword):
            raise ValueError(f"{Login.__logger}.from_copy:PasswordError")
        if not isinstance(account.Discord, Discord.DiscordUser):
            raise ValueError(f"{Login.__logger}.from_copy:DiscordError")
        return Login(
            multi_id=account.multi_id,
            task="account:check",
            student_id=account.student_id,
            discord_id=account.discord_id,
            Discord=account.Discord,
            Letus=account.Letus,
        )

    def run(self):
        session = SessionManager(self)
        session.login()
        self.push()


@dataclass
class Status(AccountTask):  # NOTE: in development
    __logger = Log("Task.AccountTask.Status")
    # [auto]
    student_id: str
    discord_id: str
    # [object]
    Discord: Discord.DiscordUser
    Letus: Letus.LetusUserWithCookies

    @classmethod
    def from_copy(cls, account: Account):
        if not isinstance(account.Letus, Letus.LetusUserWithCookies):
            raise ValueError(f"{Status.__logger}.from_copy:CookiesError")
        if not isinstance(account.Discord, Discord.DiscordUser):
            raise ValueError(f"{Status.__logger}.from_copy:DiscordError")
        return Status(
            multi_id=account.multi_id,
            task="account:status",
            student_id=account.student_id,
            discord_id=account.discord_id,
            Discord=account.Discord,
            Letus=account.Letus,
        )

    def run(self):
        print("Not supported yet")


__all__ = [
    "AccountTask",
    "Login",
    "Status",
]
