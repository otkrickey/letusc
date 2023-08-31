from dataclasses import dataclass

from pymongo import MongoClient

from letusc.logger import Log
from letusc.Model import Letus
from letusc.Model.BaseDatabase import BaseDatabase
from letusc.SessionManager import SessionManager
from letusc.URLManager import URLManager

from .AccountBase import AccountBase


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
            ("Cookie", "Letus", Letus.LetusUserWithCookies),
            ("Password", "Letus", Letus.LetusUserWithPassword),
        ]
        super().check(attrs=attrs, types=types)

    def push(self) -> None:
        try:
            super().push()
        except TypeError as e:
            if str(e) == f"{self.__logger}.check:TypeError:Cookie":
                return self.register()
            raise e

    def login(self) -> None:
        __logger = Log(f"{self.__logger}.login")
        __logger.debug("Logging in")

        session = SessionManager(self)
        session.login()
        return
