from dataclasses import dataclass
from letusc.SessionManager import SessionManager

from letusc.logger import Log
import letusc.Model.letus as Letus
import letusc.Model.discord as Discord
from letusc.Model.account import Account

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
                raise KeyError("Task.AccountTask.from_api:UnknownAction")

    def run(self):
        raise NotImplementedError("Task.AccountTask.run:NotImplemented")


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
            raise ValueError("Task.AccountTask.Login.from_copy:PasswordError")
        if not isinstance(account.Discord, Discord.DiscordUser):
            raise ValueError("Task.AccountTask.Login.from_copy:DiscordError")
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
            raise ValueError("Task.AccountTask.Status.from_copy:CookiesError")
        if not isinstance(account.Discord, Discord.DiscordUser):
            raise ValueError("Task.AccountTask.Status.from_copy:DiscordError")
        return Status(
            multi_id=account.multi_id,
            task="account:status",
            student_id=account.student_id,
            discord_id=account.discord_id,
            Discord=account.Discord,
            Letus=account.Letus,
        )

    # def run(self):
    #     self.status()
    #     self.push()


__all__ = [
    "AccountTask",
    "Login",
    "Status",
]
