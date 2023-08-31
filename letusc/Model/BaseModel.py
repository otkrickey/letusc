from dataclasses import dataclass
from typing import Callable

from letusc.logger import Log


@dataclass
class BaseModel:
    __logger = Log("Model.BaseModel")
    # Add global methods here

    def identify(self) -> None:
        self.key = "key"  # default key
        self.key_name = "key_name"  # default key_name

    def from_api(
        self, object: dict, attrs: list[tuple[str, type, Callable]] = []
    ) -> None:
        __logger = Log(f"{self.__logger}.from_api")
        try:
            for attr_name, attr_type, converter in attrs:
                converted_value = converter(object)
                if not isinstance(converted_value, attr_type):
                    raise ValueError
                setattr(self, attr_name, converted_value)
        except Exception as e:
            raise ValueError(f"{__logger}:InvalidData") from e

    def to_api(self) -> dict:
        raise NotImplementedError
