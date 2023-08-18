from dataclasses import dataclass

from letusc.logger import Log


@dataclass
class BaseModel:
    __logger = Log("Model.BaseModel")
    # Add global methods here

    def from_api(self, object: dict) -> "BaseModel":
        raise NotImplementedError

    def to_api(self) -> dict:
        raise NotImplementedError
