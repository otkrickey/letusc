from dataclasses import dataclass, field
from typing import Callable

from pymongo import MongoClient

from letusc.logger import Log
from letusc.URLManager import URLManager

from .base import BaseDatabase, BaseModel
from .discord import DiscordUser, DiscordUserBase
from .letus import (LetusUser, LetusUserBase, LetusUserWithCookies,
                    LetusUserWithPassword)


@dataclass
class AccountBase(BaseModel):
    __logger = Log("Model.AccountBase")
    multi_id: str  # 7 or 18 digit

    student_id: str = field(init=False)  # 7 digit
    discord_id: str = field(init=False)  # 18 digit
    Discord: DiscordUserBase = field(init=False)
    Letus: LetusUserBase = field(init=False)

    def identify(self) -> None:
        __logger = Log(f"{self.__logger}.identify")
        match len(self.multi_id):
            case 7:
                self.key_name = "student_id"
                self.key = self.multi_id
            case 18:
                self.key_name = "discord_id"
                self.key = self.multi_id
            case _:
                raise ValueError(f"{__logger}:InvalidMultiID")

    def from_api(
        self, object: dict, attrs: list[tuple[str, type, Callable]] = []
    ) -> None:
        attrs[:0] = [
            ("student_id", str, lambda obj: obj["student_id"]),
            ("discord_id", str, lambda obj: obj["discord_id"]),
            ("Letus", LetusUser, lambda obj: LetusUser.from_api(obj)),
            ("Discord", DiscordUser, lambda obj: DiscordUser.from_api(obj)),
        ]
        super().from_api(object, attrs=attrs)

    def to_api(self) -> dict:
        return {
            "student_id": self.student_id,
            "discord_id": self.discord_id,
            "Letus": self.Letus.to_api(),
            "Discord": self.Discord.to_api(),
        }


@dataclass
class AccountDatabase(BaseDatabase, AccountBase):
    __logger = Log("Model.Account.Database")
    collection = MongoClient(URLManager.getMongo())["letus"]["accountsV2"]

    def check(
        self, attrs: list[str] = [], types: list[tuple[str, str, type]] = []
    ) -> None:
        attrs[:0] = ["multi_id", "student_id", "discord_id", "Letus", "Discord"]
        types[:0] = [
            ("StudentID", "student_id", str),
            ("DiscordID", "discord_id", str),
            ("Cookie", "Letus", LetusUserWithCookies),
            ("Password", "Letus", LetusUserWithPassword),
        ]
        super().check(attrs=attrs, types=types)

    def push(self) -> None:
        try:
            super().push()
        except TypeError as e:
            if str(e) == f"{self.__logger}.check:TypeError:Cookie":
                return self.register()
            raise e


@dataclass
class Account(AccountDatabase, AccountBase):
    __logger = Log("Model.Account")

    def __post_init__(self):
        self.identify()
        object = self.pull()
        self.from_api(object)


__all__ = [
    "AccountBase",
    "AccountDatabase",
    "Account",
]
