from dataclasses import dataclass

from pymongo import MongoClient
from pymongo.errors import WriteError

from letusc.logger import Log
from letusc.Model.BaseDatabase import BaseDatabase
from letusc.util.static import mongo_url

from .ModuleBase import ModuleBase


@dataclass
class ModuleDatabase(BaseDatabase, ModuleBase):
    __logger = Log("Model.Module.Database")
    collection = MongoClient(mongo_url())["letus"]["modules"]

    def check(self) -> None:
        __logger = Log("Model.Module.Database.check")
        __logger.debug("Checking module info")
        attributes = ["code", "title", "main", "modules", "hash", "timestamp"] # TODO: Check this
        if any(hasattr(self, attribute) for attribute in attributes):
            __logger.info("Attribute Error")
            raise ValueError("Model.Module.Database.check:AttributeError")
        __logger.info("Module is valid")
        return

    def pull(self) -> dict:
        __logger = Log("Model.Module.Database.pull")
        __logger.debug("Pulling module info from MongoDB")
        filter = {}
        filter.update({"code": self.code})
        object = self.collection.find_one(filter)
        if object is None:
            __logger.info("No data found")
            raise ValueError("Model.Module.Database.pull:NotFound")
        return object

    def push(self) -> None:
        __logger = Log("Model.Module.Database.push")
        __logger.debug("Pushing module info to MongoDB")
        try:
            self.check()
            self.update()
        except ValueError as e:
            match str(e):
                case "Model.Module.Database.update:WriteError":
                    return self.register()
                case _:
                    raise e
        return

    def register(self) -> None:
        __logger = Log("Model.Module.Database.register")
        __logger.debug("Registering module info")
        try:
            self.collection.insert_one(self.to_api())
        except WriteError as e:
            raise ValueError("Model.Module.Database.register:WriteError") from e
        return

    def update(self) -> None:
        __logger = Log("Model.Module.Database.update")
        __logger.debug("Updating module info")
        try:
            self.collection.update_one({"code": self.code}, {"$set": self.to_api()})
        except WriteError as e:
            raise ValueError("Model.Module.Database.update:WriteError") from e
        return
