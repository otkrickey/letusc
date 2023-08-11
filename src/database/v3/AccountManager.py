from pymongo import MongoClient
from pymongo.errors import WriteError

from src.Letus.LetusAccount import LetusAccount
from src.util.logger import Logger, Log
from src.util.static import mongo_url


class AccountManager:
    def __init__(self, LA: LetusAccount):
        self.LA = LA
        self.client = MongoClient(mongo_url())
        self.db = self.client["letus"]
        self.collection = self.db["accounts"]

    def check(self):
        __logger = Log("AccountManager.check")
        __logger.debug("Checking account info")
        if not self.LA.sync:
            __logger.info("Account not synced")
            self.pull()
            return self.check()
        if self.LA.email is None:
            __logger.error("Email Error")
            raise ValueError("AccountManager:check:EmailError")
        if self.LA.encrypted_password is None:
            __logger.error("Password Error")
            raise ValueError("AccountManager:check:PasswordError")
        if (self.LA.cookie is None) or (not self.LA.cookie):
            __logger.info("Cookie Error")
            raise ValueError("AccountManager:check:CookieError")
        __logger.debug("Account info checked")
        return

    def pull(self):
        __logger = Log("AccountManager.pull")
        __logger.debug("Fetching account")
        filter = {"discord_id": self.LA.discord_id}
        account = self.collection.find_one(filter)
        if account is None:
            __logger.info("Account not found")
            raise ValueError("AccountManager:pull:NotFound")
        try:
            self.LA.email = account["email"]
            self.LA.encrypted_password = account["encrypted_password"]
            self.LA.cookie = account["cookie"]
            if (self.LA.cookie is None) or (not self.LA.cookie):
                __logger.info("There is no available cookie")
                raise ValueError("AccountManager:pull:CookieError")
        except KeyError:
            __logger.info("Account could not be fetched correctly")
            raise KeyError("AccountManager:pull:KeyError")
        else:
            self.LA.sync = True
            __logger.debug("Account found")
            return

    def push(self):
        __logger = Log("AccountManager.push")
        __logger.debug("Pushing account")
        try:
            self.check()
        except ValueError as e:
            if "AccountManager:pull:NotFound" in str(e):
                return self.register()
            else:
                raise e
        else:
            return self.update()

    def register(self):
        __logger = Log("AccountManager.register")
        __logger.debug("Registering account")
        LAO = self.LA.export()
        try:
            __logger.debug("Creating account")
            self.collection.insert_one(LAO)
        except WriteError:
            __logger.info("Account could not be registered correctly")
            raise WriteError("AccountManager:register:WriteError")
        else:
            __logger.debug("Account registered")
            return

    def update(self):
        __logger = Log("AccountManager.update")
        __logger.debug("Updating account")
        filter = {"discord_id": self.LA.discord_id}
        update = {
            "$set": {
                "email": self.LA.email,
                "encrypted_password": self.LA.encrypted_password,
                "cookie": self.LA.cookie,
            }
        }
        try:
            __logger.debug("Updating account")
            self.collection.update_one(filter, update)
        except WriteError:
            __logger.info("Account could not be updated correctly")
            raise WriteError("AccountManager:update:WriteError")
        else:
            __logger.debug("Account updated")
            return
