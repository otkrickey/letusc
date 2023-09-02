from dataclasses import dataclass, field
from typing import Callable

from pymongo.collection import Collection

from letusc.logger import Log


@dataclass
class BaseModel:
    _logger = Log("Model.BaseModel")
    # Add global methods here

    def identify(self) -> None:
        self.key = "key"  # default key
        self.key_name = "key_name"  # default key_name

    def from_api(
        self, object: dict, attrs: list[tuple[str, type, Callable]] = []
    ) -> None:
        _logger = Log(f"{BaseModel._logger}.from_api")
        try:
            for attr_name, attr_type, converter in attrs:
                converted_value = converter(object)
                if not isinstance(converted_value, attr_type):
                    raise ValueError
                setattr(self, attr_name, converted_value)
        except Exception as e:
            raise ValueError(f"{_logger}:InvalidData") from e

    def to_api(self) -> dict:
        raise NotImplementedError


@dataclass
class BaseDatabase(BaseModel):
    _logger = Log("Model.BaseDatabase")
    collection: Collection = field(init=False)

    def check(
        self, attrs: list[str] = [], types: list[tuple[str, str, type]] = []
    ) -> None:
        _logger = Log(f"{BaseDatabase._logger}.check")
        if any(not hasattr(self, attr) for attr in attrs):
            _logger.info("Attribute Error")
            raise ValueError(f"{_logger}:AttributeError")
        for err_key, attr, attr_type in types:
            if not isinstance(getattr(self, attr, None), attr_type):
                _logger.info(f"Type Error: {attr}={getattr(self, attr, None)}")
                raise TypeError(f"{_logger}:TypeError:{err_key}")
        _logger.info(f"Valid: {self.key_name}={self.key}")
        return

    def pull(self) -> dict:
        _logger = Log(f"{BaseDatabase._logger}.pull")
        _logger.debug(f"Pull {self.key_name}={self.key}")
        filter = {}
        filter.update({self.key_name: self.key})
        object = self.collection.find_one(filter)
        if object is None:
            _logger.info("No data found")
            raise ValueError(f"{_logger}:NotFound")
        return object

    def push(self) -> None:
        _logger = Log(f"{BaseDatabase._logger}.push")
        _logger.debug(f"Push {self.key_name}={self.key}")
        try:
            self.check()
            self.pull()
        except ValueError as e:
            if str(e) == f"{BaseDatabase._logger}.pull:NotFound":
                return self.register()
            raise e
        else:
            self.update()
        return

    def register(self) -> None:
        _logger = Log(f"{BaseDatabase._logger}.register")
        _logger.debug(f"Register {self.key_name}={self.key}")
        try:
            self.collection.insert_one(self.to_api())
        except Exception as e:
            raise ValueError(f"{_logger}:DatabaseError") from e
        return

    def update(self) -> None:
        _logger = Log(f"{BaseDatabase._logger}.update")
        _logger.debug(f"Update {self.key_name}={self.key}")
        try:
            self.collection.update_one(
                {self.key_name: self.key}, {"$set": self.to_api()}, upsert=True
            )
        except Exception as e:
            raise ValueError(f"{_logger}:DatabaseError") from e
        return
