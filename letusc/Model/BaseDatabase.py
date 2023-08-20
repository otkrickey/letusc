from dataclasses import dataclass, field

from pymongo.collection import Collection

from letusc.logger import Log
from letusc.Model.BaseModel import BaseModel


@dataclass
class BaseDatabase(BaseModel):
    __logger = Log("Model.BaseDatabase")
    collection: Collection = field(init=False)

    def check(self) -> None:
        raise NotImplementedError("Model.BaseDatabase.check:NotImplementedError")

    def pull(self) -> dict:
        raise NotImplementedError("Model.BaseDatabase.pull:NotImplementedError")

    def push(self) -> None:
        raise NotImplementedError("Model.BaseDatabase.push:NotImplementedError")

    def register(self) -> None:
        raise NotImplementedError("Model.BaseDatabase.register:NotImplementedError")

    def update(self) -> None:
        raise NotImplementedError("Model.BaseDatabase.update:NotImplementedError")

    def login(self) -> None:
        raise NotImplementedError("Model.BaseDatabase.login:NotImplementedError")
