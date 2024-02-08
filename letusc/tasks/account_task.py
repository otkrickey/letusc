from dataclasses import dataclass, field

from ..authenticator import Authenticator
from ..chat import DiscordChatUser
from ..logger import get_logger
from ..models.account import Account, NewAccount
from ..models.discord import DiscordUser, DiscordUserAny
from ..models.letus import LetusUserWithPassword
from .base_task import TaskBase

logger = get_logger(__name__)

__all__ = [
    "AccountTaskBase",
    "RegisterAccountTask",
    "LoginAccountTask",
]


class AccountTaskBase(TaskBase):
    task: str
    multi_id: str

    @staticmethod
    async def from_api(task: dict) -> "AccountTaskBase":
        action = task["task"].split(":")[1]
        match action:
            case "login":
                return await LoginAccountTask.from_api(task)
            case "register":
                return await RegisterAccountTask.from_api(task)
            case _:
                raise KeyError(logger.c("UnknownAction"))


@dataclass
class RegisterAccountTask(AccountTaskBase):
    task: str = field(init=False, default="account:register")
    multi_id: str = field(init=False)
    student_id: str
    discord_id: str
    password: str
    username: str
    discriminator: str
    Letus: LetusUserWithPassword = field(init=False)
    Discord: DiscordUserAny = field(init=False)

    def __post_init__(self):
        self.multi_id = self.discord_id
        self.Letus = LetusUserWithPassword(
            student_id=self.student_id,
            password=self.password,
        )
        self.Discord = DiscordUser(
            discord_id=self.discord_id,
            username=self.username,
            discriminator=self.discriminator,
        )

    @classmethod
    async def from_api(cls, task: dict) -> "RegisterAccountTask":
        return cls(
            student_id=task["student_id"],
            discord_id=task["discord_id"],
            password=task["password"],
            username=task["username"],
            discriminator=task["discriminator"],
        )

    async def run(self):
        logger.info("Registering account")
        account = NewAccount.create(
            student_id=self.student_id,
            discord_id=self.discord_id,
            password=self.password,
            username=self.username,
            discriminator=self.discriminator,
        )
        await Authenticator(account).register()
        await account.push()
        chat = await DiscordChatUser.get(int(self.discord_id))
        await chat.SendMessage("Letusにログインしました。")


@dataclass
class LoginAccountTask(AccountTaskBase):
    task: str = field(init=False, default="account:login")
    multi_id: str

    @classmethod
    async def from_api(cls, task: dict) -> "LoginAccountTask":
        return cls(
            multi_id=task["discord_id"],
        )

    async def run(self):  # TODO: fix this
        account = Account(self.multi_id)
        # _SessionManager(account).login()
        # account.push()


@dataclass
class RegisterAccountLoopTask(AccountTaskBase):
    task: str = field(init=False, default="account:register")
    account: Account

    @classmethod
    async def create(cls, object: dict):
        account = Account(object["student_id"])
        account.from_api(object)
        return cls(
            account=account,
        )

    async def run(self):
        logger.info("Registering account")

        await Authenticator(self.account).register()
        await self.account.push()
        chat = await DiscordChatUser.get(int(self.account.discord_id))
        await chat.SendMessage("Letusにログインしました。")
