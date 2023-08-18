import logging
from dataclasses import dataclass, field
from typing import Union

from pymongo import MongoClient
from pymongo.errors import WriteError

from letusc import Session
from letusc.logger import Log
from letusc.util.static import mongo_url

from .discord import DiscordMessage, DiscordUser, DiscordUserFull
from .letus import Cookie, LetusUser, LetusUserWithCookies, LetusUserWithPassword

__all__ = [
    "Account",
    # Discord
    "DiscordUser",
    "DiscordUserFull",
    "DiscordMessage",
    # Letus
    "LetusUser",
    "LetusUserWithPassword",
    "LetusUserWithCookies",
    "Cookie",
]


@dataclass
class Account:
    __logger = Log("Model.Account")
    collection = MongoClient(mongo_url())["letus"]["accountsV2"]
    # [must]
    multi_id: str  # 7 or 18 digit
    # [optional]
    student_id: str = field(init=False)  # 7 digit
    discord_id: str = field(init=False)  # 18 digit
    # [object]
    Discord: Union[DiscordUser, DiscordUserFull] = field(init=False)
    Letus: Union[LetusUser, LetusUserWithCookies, LetusUserWithPassword] = field(
        init=False
    )

    def __post_init__(self):
        account = self.pull()
        self.student_id = account["student_id"]
        self.discord_id = account["discord_id"]
        self.Letus = LetusUser.from_api(account)
        self.Discord = DiscordUser.from_api(account)

    def check(self):
        __logger = Log("Model.Account.check")
        __logger.debug("Checking account info")
        if isinstance(self.Letus, LetusUserWithPassword):
            __logger.info("Cookie Error")
            raise ValueError("Model.Account.check:CookieError")
        if isinstance(self.Letus, LetusUser):
            __logger.info("Password Error")
            raise ValueError("Model.Account.check:PasswordError")
        __logger.info("Account is valid")
        return

    def pull(self) -> dict:
        __logger = Log("Model.Account.pull")
        __logger.debug("Pulling data from MongoDB")
        filter = {}
        match len(self.multi_id):
            case 7:
                self.student_id = self.multi_id
                filter.update({"student_id": self.student_id})
            case 18:
                self.discord_id = self.multi_id
                filter.update({"discord_id": self.discord_id})
            case _:
                raise ValueError("Invalid multi_id")
        account = self.collection.find_one(filter)
        if account is None:
            __logger.info("No data found")
            raise ValueError("Model.Account.pull:NotFound")
        return account

    def push(self):
        __logger = Log("Model.Account.push")
        __logger.debug("Pushing data to MongoDB")
        try:
            self.check()
        except ValueError as e:
            match str(e):
                case "Model.Account.check:CookieError":
                    return self.register()
                case _:
                    raise e
        else:
            return self.update()

    def register(self):
        __logger = Log("Model.Account.register")
        __logger.debug("Registering new account")
        try:
            self.collection.insert_one(self.export())
        except WriteError as e:
            __logger.info("Account could not be registered correctly")
            raise WriteError("Model.Account.register:WriteError")
        else:
            __logger.debug("Account registered")
            return

    def export(self):
        return {
            "student_id": self.student_id,
            "discord_id": self.discord_id,
            "Letus": self.Letus.to_api(),
            "Discord": self.Discord.to_api(),
        }

    def update(self):
        __logger = Log("Model.Account.update")
        __logger.debug("Updating account")
        filter = {
            "discord_id": self.discord_id,
        }
        update = {
            "$set": {
                "Letus": self.Letus.to_api(),
            },
        }
        try:
            __logger.debug("Updating account")
            self.collection.update_one(filter, update)
        except WriteError:
            __logger.info("Account could not be updated correctly")
            raise WriteError("Model.Account.update:WriteError")
        else:
            __logger.debug("Account updated")
            return

    def login(self):
        __logger = Log("Model.Task.Account.login")
        session = Session.Manager(self)
        try:
            session.login()
        except TimeoutError as e:
            match str(e):
                case "Session.Automator.login_letus:Timeout":
                    raise e
        except ValueError as e:
            match str(e):
                case "Session.Automator.login_letus:PasswordError":
                    raise e
        except Exception as e:
            logging.error(e)
            raise Exception("Model.Task.Account.login:UnknownError")
        else:
            __logger.info("Logged in successfully")
