from dataclasses import dataclass, field

from ..authenticator import Authenticator
from ..chat import DiscordChatUser
from ..logger import L
from ..models.account import Account, NewAccount
from ..models.discord import DiscordUser, DiscordUserAny
from ..models.letus import LetusUserWithPassword
from .base_task import TaskBase

__all__ = [
    "AccountTaskBase",
    "RegisterAccountTask",
    "LoginAccountTask",
]


class AccountTaskBase(TaskBase):
    _l = L()
    task: str
    multi_id: str

    @staticmethod
    async def from_api(task: dict) -> "AccountTaskBase":
        _l = L(AccountTaskBase.__name__).gm("from_api")
        action = task["task"].split(":")[1]
        match action:
            case "login":
                return await LoginAccountTask.from_api(task)
            case "register":
                return await RegisterAccountTask.from_api(task)
            case _:
                raise KeyError(_l.c("UnknownAction"))


@dataclass
class RegisterAccountTask(AccountTaskBase):
    _l = L()
    task: str = field(init=False, default="account:register")
    multi_id: str = field(init=False)
    student_id: str
    discord_id: str
    encrypted_password: str
    username: str
    discriminator: str
    Letus: LetusUserWithPassword = field(init=False)
    Discord: DiscordUserAny = field(init=False)

    def __post_init__(self):
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")
        self.multi_id = self.discord_id
        self.Letus = LetusUserWithPassword(
            student_id=self.student_id,
            encrypted_password=self.encrypted_password,
        )
        self.Discord = DiscordUser(
            discord_id=self.discord_id,
            username=self.username,
            discriminator=self.discriminator,
        )

    @classmethod
    async def from_api(cls, task: dict) -> "RegisterAccountTask":
        _l = L(cls.__name__).gm("from_api")
        return cls(
            student_id=task["student_id"],
            discord_id=task["discord_id"],
            encrypted_password=task["encrypted_password"],
            username=task["username"],
            discriminator=task["discriminator"],
        )

    async def run(self):
        _l = self._l.gm("run")
        _l.info("Registering account")
        account = NewAccount.create(
            student_id=self.student_id,
            discord_id=self.discord_id,
            encrypted_password=self.encrypted_password,
            username=self.username,
            discriminator=self.discriminator,
        )
        await Authenticator(account).register()
        await account.push()
        chat = await DiscordChatUser.get(int(self.discord_id))
        await chat.SendMessage("Letusにログインしました。")


@dataclass
class LoginAccountTask(AccountTaskBase):
    _l = L()
    task: str = field(init=False, default="account:login")
    multi_id: str

    @classmethod
    async def from_api(cls, task: dict) -> "LoginAccountTask":
        _l = L(cls.__name__).gm("from_api")
        return cls(
            multi_id=task["discord_id"],
        )

    async def run(self):  # TODO: fix this
        _l = self._l.gm("run")
        account = Account(self.multi_id)
        # _SessionManager(account).login()
        # account.push()
