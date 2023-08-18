from dataclasses import dataclass

from pymongo import MongoClient
from pymongo.errors import WriteError

from letusc.logger import Log
from letusc.Model.Letus import LetusUser, LetusUserWithPassword
from letusc.SessionManager import SessionManager
from letusc.util.static import mongo_url

from .AccountBase import AccountBase


@dataclass
class Database(AccountBase):
    __logger = Log("Model.Database")
    collection = MongoClient(mongo_url())["letus"]["accountsV2"]

    def check(self):
        __logger = Log("Model.Account.Database.check")
        __logger.debug("Checking account info")
        if isinstance(self.Letus, LetusUserWithPassword):
            __logger.info("Cookie Error")
            raise ValueError("Model.Account.Database.check:CookieError")
        if isinstance(self.Letus, LetusUser):
            __logger.info("Password Error")
            raise ValueError("Model.Account.Database.check:PasswordError")
        __logger.info("Account is valid")
        return

    def pull(self) -> dict:
        __logger = Log("Model.Account.Database.pull")
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
        except ValueError as e:
            match str(e):
                case "Model.Account.Database.check:CookieError":
                    return self.register()
                case _:
                    raise e
        else:
            return self.update()

    def register(self) -> None:
        __logger = Log("Model.Account.Database.register")
        __logger.debug("Registering new account")
        try:
            self.collection.insert_one(self.to_api())
        except WriteError as e:
            __logger.error(f"Failed to register new account: {e}")
            raise WriteError("Model.Account.Database.push:WriteError")
        else:
            __logger.debug("Account registered")
            return

    def update(self) -> None:
        __logger = Log("Model.Account.Database.update")
        __logger.debug("Updating account")
        filter = {"discord_id": self.discord_id}
        update = {"$set": self.to_api()}
        try:
            __logger.debug("Updating account")
            self.collection.update_one(filter, update)
        except WriteError as e:
            __logger.error(f"Failed to update account: {e}")
            raise WriteError("Model.Account.Database.update:WriteError")
        else:
            __logger.debug("Account updated")
            return

    def login(self) -> None:
        __logger = Log("Model.Account.Database.login")
        __logger.debug("Logging in")

        session = SessionManager(self)
        session.login()
        return
