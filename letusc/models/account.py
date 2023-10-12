from dataclasses import dataclass, field

from ..db import DBManager
from ..logger import get_logger
from .base import BaseDatabase, BaseModel, attrs, from_api_attrs, to_api_attrs, types
from .cookie import Cookie
from .discord import DiscordUser, DiscordUserAny, DiscordUserBase
from .letus import LetusUser, LetusUserBase, LetusUserWithCookies, LetusUserWithPassword

logger = get_logger(__name__)

__all__ = [
    "AccountBase",
    "Account",
    "NewAccount",
]


@dataclass
class AccountBase(BaseDatabase, BaseModel):
    _attrs = BaseModel._attrs | attrs(
        ["multi_id", "student_id", "discord_id", "Letus", "Discord"]
    )
    _types = BaseModel._types | types(
        [
            ("student_id", "StudentID", str),
            ("discord_id", "DiscordID", str),
            ("Letus", "LetusUser", LetusUser),
            ("Letus", "LetusUserWithPassword", LetusUserWithPassword),
            ("Letus", "LetusUserWithCookies", LetusUserWithCookies),
            ("Discord", "DiscordUserAny", DiscordUserAny),
            ("Discord", "DiscordUser", DiscordUser),
        ]
    )
    _from_api_attrs = BaseModel._from_api_attrs | from_api_attrs(
        [
            ("student_id", str, lambda obj: obj["student_id"]),
            ("discord_id", str, lambda obj: obj["discord_id"]),
            ("Letus", LetusUser, lambda obj: LetusUser.from_api(obj)),
            ("Discord", DiscordUser, lambda obj: DiscordUser.from_api(obj)),
        ]
    )
    _to_api_attrs = BaseModel._to_api_attrs | to_api_attrs(
        [
            ("student_id", lambda self: self.student_id),
            ("discord_id", lambda self: self.discord_id),
            ("Letus", lambda self: self.Letus.to_api()),
            ("Discord", lambda self: self.Discord.to_api()),
        ]
    )

    multi_id: str
    collection = DBManager.get_collection("letus", "accounts")

    student_id: str = field(init=False)
    discord_id: str = field(init=False)
    Letus: LetusUserBase = field(init=False)
    Discord: DiscordUserBase = field(init=False)

    def __post_init__(self):
        BaseModel.__post_init__(self)
        match len(self.multi_id):
            case 7:
                self.key_name = "student_id"
                self.key = self.multi_id
            case 18:
                self.key_name = "discord_id"
                self.key = self.multi_id
            case _:
                raise ValueError(logger.c("InvalidMultiID"))

    def get_cookie(self, year: str) -> Cookie:
        try:
            self.check()
        except TypeError as e:
            if (
                f"{self.__class__.__name__}.check:TypeError:LetusUserWithCookies"
                in str(e)
            ):
                raise Exception(logger.c("NoCookies")) from e
        finally:
            assert isinstance(self.Letus, LetusUserWithCookies)
            for cookie in self.Letus.cookies:
                if cookie.year == year:
                    return cookie
            else:
                raise Exception(logger.c("NoCookies"))

    async def push(self) -> None:
        try:
            self.check()
        except TypeError as e:
            if (
                f"{self.__class__.__name__}.check:TypeError:LetusUserWithCookies"
                in str(e)
            ):
                pass
            elif f"{self.__class__.__name__}.check:TypeError:DiscordUser" in str(e):
                pass
            else:
                raise e
        finally:
            await BaseDatabase.push(self)


@dataclass
class Account(AccountBase):
    def __post_init__(self):
        AccountBase.__post_init__(self)

    @classmethod
    async def pull(cls, multi_id: str) -> "Account":
        account = cls(multi_id=multi_id)
        object = await account._pull()
        account.from_api(object)
        return account


@dataclass
class NewAccount(AccountBase):
    multi_id: str = field(init=False)
    student_id: str
    discord_id: str
    Letus: LetusUserWithPassword
    Discord: DiscordUserAny

    def __post_init__(self):
        self.multi_id = self.discord_id
        AccountBase.__post_init__(self)

    @classmethod
    def create(
        cls,
        student_id: str,
        discord_id: str,
        encrypted_password: str,
        username: str,
        discriminator: str,
    ) -> "NewAccount":
        return cls(
            student_id=student_id,
            discord_id=discord_id,
            Letus=LetusUserWithPassword(
                student_id=student_id,
                encrypted_password=encrypted_password,
            ),
            Discord=DiscordUser(
                discord_id=discord_id,
                username=username,
                discriminator=discriminator,
            ),
        )
