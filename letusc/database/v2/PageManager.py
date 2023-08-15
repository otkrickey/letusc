from pymongo import MongoClient
from pymongo.errors import WriteError

from src.Letus.v2.LetusPage import LetusPage
from src.util.logger import Logger


class PageManager:
    def __init__(self, LP: LetusPage) -> None:
        self.LP = LP
        self.client = MongoClient(
            "mongodb+srv://otkrickey:Tm6Mp291LJwFIscK@letus.tcigkrt.mongodb.net/?retryWrites=true&w=majority"
        )
        self.db = self.client["letus"]
        self.collection = self.db["pages"]

        self.__logger = Logger(self.__class__.__name__)

    def check(self):
        self.__logger.emit(
            "PageManager:check:Start", "202", "Checking Page Info", self.check.__name__
        )
        try:
            if not self.LP.sync:
                self.__logger.emit(
                    "PageManager:check:SyncError",
                    "401",
                    "Page not synced",
                    self.check.__name__,
                )
                raise ValueError("PageManager:check:SyncError")
        except ValueError:
            self.pull()
            return self.check()
        else:
            self.__logger.emit(
                "PageManager:check:Success", "200", "Page found", self.check.__name__
            )
            return

    def pull(self):
        self.__logger.emit(
            "PageManager:pull:Start",
            "202",
            "Fetching Page Info Start",
            self.pull.__name__,
        )
        filter = {
            "key": self.LP.key,
        }
        page = self.collection.find_one(filter)
        if page is None:
            self.__logger.emit(
                "PageManager:pull:NotFound", "404", "Page not found", self.pull.__name__
            )
            raise ValueError("PageManager:pull:NotFound")
        try:
            self.LP.code = page["code"]
            self.LP.accounts = page["accounts"]
        except KeyError:
            self.__logger.emit(
                "PageManager:pull:KeyError",
                "500",
                "Page could not be fetched correctly",
                self.pull.__name__,
            )
            raise KeyError("PageManager:pull:KeyError")
        else:
            self.LP.struct()
            self.LP.sync = True
            self.__logger.emit(
                "PageManager:pull:Success", "200", "Page found", self.pull.__name__
            )
            return

    def push(self):
        self.__logger.emit(
            "PageManager:push:Start",
            "202",
            "Fetching Page Info Start",
            self.push.__name__,
        )
        try:
            self.check()
        except ValueError as e:
            if "PageManager:pull:NotFound" in str(e):
                return self.register()
            else:
                raise e
        else:
            return self.update()

    def register(self):
        self.__logger.emit(
            "PageManager:register:Start",
            "202",
            "Fetching Page Info Start",
            self.register.__name__,
        )
        LPO = self.LP.export()
        try:
            self.__logger.emit(
                "PageManager:register:Creating",
                "202",
                "Creating Page",
                self.register.__name__,
            )
            self.collection.insert_one(LPO)
        except WriteError:
            self.__logger.emit(
                "PageManager:register:WriteError",
                "500",
                "Page could not be created",
                self.register.__name__,
            )
            raise WriteError("PageManager:register:WriteError")
        else:
            self.LP.sync = True
            self.__logger.emit(
                "PageManager:register:Success",
                "200",
                "Page created",
                self.register.__name__,
            )
            return

    def update(self):
        self.__logger.emit(
            "PageManager:update:Start",
            "202",
            "Fetching Page Info Start",
            self.update.__name__,
        )
        filter = {
            "code": self.LP.code,
        }
        update = {"$set": {"accounts": self.LP.accounts}}
        try:
            self.__logger.emit(
                "PageManager:update:Updating",
                "202",
                "Updating Page",
                self.update.__name__,
            )
            self.collection.update_one(filter, update)
        except WriteError:
            self.__logger.emit(
                "PageManager:update:WriteError",
                "500",
                "Page could not be updated",
                self.update.__name__,
            )
            raise WriteError("PageManager:update:WriteError")
        else:
            self.LP.sync = True
            self.__logger.emit(
                "PageManager:update:Success",
                "200",
                "Page updated",
                self.update.__name__,
            )
            return
