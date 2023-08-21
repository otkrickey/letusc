from dataclasses import dataclass

from pymongo import MongoClient
from pymongo.errors import WriteError

from letusc.logger import Log
from letusc.Model.BaseDatabase import BaseDatabase
from letusc.util.static import mongo_url

from .ContentBase import ContentBase


@dataclass
class ContentDatabase(BaseDatabase, ContentBase):
    __logger = Log("Model.Content.Database")
    collection = MongoClient(mongo_url())["letus"]["contents"]

    def check(self) -> None:
        __logger = Log("Model.Content.Database.check")
        __logger.debug("Checking content info")
        attributes = ["code", "title", "main", "modules", "hash", "timestamp"]
        if any(hasattr(self, attribute) for attribute in attributes):
            __logger.info("Attribute Error")
            raise ValueError("Model.Content.Database.check:AttributeError")
        __logger.info("Content is valid")
        return

    def pull(self) -> dict:
        __logger = Log("Model.Content.Database.pull")
        __logger.debug("Pulling content info from MongoDB")
        filter = {}
        filter.update({"code": self.code})
        object = self.collection.find_one(filter)
        if object is None:
            __logger.info("No data found")
            raise ValueError("Model.Content.Database.pull:NotFound")
        return object

    def push(self) -> None:
        __logger = Log("Model.Content.Database.push")
        __logger.debug("Pushing content info to MongoDB")
        try:
            self.check()
            self.update()
        except ValueError as e:
            match str(e):
                case "Model.Content.Database.update:WriteError":
                    return self.register()
                case _:
                    raise e
        return

    def register(self) -> None:
        __logger = Log("Model.Content.Database.register")
        __logger.debug("Registering content info")
        try:
            self.collection.insert_one(self.to_api())
        except WriteError as e:
            raise ValueError("Model.Content.Database.register:WriteError") from e
        return

    def update(self) -> None:
        __logger = Log("Model.Content.Database.update")
        __logger.debug("Updating content info")
        try:
            self.collection.update_one({"code": self.code}, {"$set": self.to_api()})
        except WriteError as e:
            raise ValueError("Model.Content.Database.update:WriteError") from e
        return
