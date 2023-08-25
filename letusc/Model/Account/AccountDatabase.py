from dataclasses import dataclass

from pymongo import MongoClient
from pymongo.errors import WriteError

from letusc.logger import Log
from letusc.Model import Letus
from letusc.Model.BaseDatabase import BaseDatabase
from letusc.SessionManager import SessionManager
from letusc.util.static import mongo_url

from .AccountBase import AccountBase


@dataclass
class AccountDatabase(BaseDatabase, AccountBase):
    __logger = Log("Model.Account.Database")
    collection = MongoClient(mongo_url())["letus"]["accountsV2"]

    def check(self):
        __logger = Log("Model.Account.Database.check")
        __logger.debug("Checking account info")
        attributes = ["multi_id", "student_id", "discord_id", "Letus", "Discord"]
        if any(hasattr(self, attribute) for attribute in attributes):
            __logger.info("Attribute Error")
            raise ValueError("Model.Account.Database.check:AttributeError")
        if not isinstance(self.Letus, Letus.LetusUserWithCookies):
            __logger.info("Cookie Error")
            raise ValueError("Model.Account.Database.check:CookieError")
        elif not isinstance(self.Letus, Letus.LetusUserWithPassword):
            __logger.info("Password Error")
            raise ValueError("Model.Account.Database.check:PasswordError")
        __logger.info("Account is valid")
        return

    def pull(self) -> dict:
        __logger = Log("Model.Account.Database.pull")
        __logger.debug(f"Pulling data from MongoDB: {self.multi_id}")
        filter = {}
        match len(self.multi_id):
            case 7:
                self.student_id = self.multi_id
                filter.update({"student_id": self.student_id})
            case 18:
                self.discord_id = self.multi_id
                filter.update({"discord_id": self.discord_id})
            case _:
                raise ValueError("Model.Account.Database.pull:InvalidMultiID")
        object = self.collection.find_one(filter)
        if object is None:
            __logger.info("No data found")
            raise ValueError("Model.Account.Database.pull:NotFound")
        return object

    def push(self) -> None:
        __logger = Log("Model.Account.Database.push")
        __logger.debug("Pushing data to MongoDB")
        try:
            self.check()
            self.update()
        except ValueError as e:
            match str(e):
                case "Model.Account.Database.check:CookieError":
                    return self.register()
                case "Model.Account.Database.update:WriteError":
                    return self.register()
                case _:
                    raise e
        return

    def register(self) -> None:
        __logger = Log("Model.Account.Database.register")
        __logger.debug("Registering account info")
        try:
            self.collection.insert_one(self.to_api())
        except WriteError as e:
            raise WriteError("Model.Account.Database.push:WriteError") from e
        return

    def update(self) -> None:
        __logger = Log("Model.Account.Database.update")
        __logger.debug("Updating account")
        try:
            self.collection.replace_one({"discord_id": self.discord_id}, self.to_api())
        except WriteError as e:
            raise WriteError("Model.Account.Database.update:WriteError") from e
        return

    def login(self) -> None:
        __logger = Log("Model.Account.Database.login")
        __logger.debug("Logging in")

        session = SessionManager(self)
        session.login()
        return
