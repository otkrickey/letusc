from dataclasses import dataclass

from pymongo import MongoClient
from pymongo.errors import WriteError

from letusc.logger import Log
from letusc.Model.BaseDatabase import BaseDatabase
from letusc.util.static import mongo_url

from .PageBase import PageBase


@dataclass
class PageDatabase(BaseDatabase, PageBase):
    __logger = Log("Model.Page.Database")
    collection = MongoClient(mongo_url())["letus"]["pagesV2"]

    def check(self) -> None:
        __logger = Log("Model.Page.Database.check")
        __logger.debug("Checking page info")
        attributes = ["code", "accounts", "title", "contents", "hash", "timestamp"]
        if any(not hasattr(self, attribute) for attribute in attributes):
            __logger.info("Attribute Error")
            raise ValueError("Model.Page.Database.check:AttributeError")
        __logger.info("Page is valid")
        return

    def pull(self) -> dict:
        __logger = Log("Model.Page.Database.pull")
        __logger.debug(f"Pulling page info from MongoDB: {self.code}")
        filter = {}
        filter.update({"code": self.code})
        object = self.collection.find_one(filter)
        if object is None:
            __logger.info("No data found")
            raise ValueError("Model.Page.Database.pull:NotFound")
        return object

    def push(self) -> None:
        __logger = Log("Model.Page.Database.push")
        __logger.debug("Pushing page info to MongoDB")
        try:
            self.check()
            self.pull()
        except ValueError as e:
            match str(e):
                case "Model.Page.Database.pull:NotFound":
                    return self.register()
                case _:
                    raise e
        else:
            self.update()
        return

    def register(self) -> None:
        __logger = Log("Model.Page.Database.register")
        __logger.debug("Registering page info")
        try:
            self.collection.insert_one(self.to_api())
        except WriteError as e:
            raise ValueError("Model.Page.Database.register:WriteError") from e
        return

    def update(self) -> None:
        __logger = Log("Model.Page.Database.update")
        __logger.debug("Updating page info")
        try:
            self.collection.replace_one({"code": self.code}, self.to_api())
        except WriteError as e:
            raise WriteError("Model.Page.Database.update:WriteError") from e
        return
