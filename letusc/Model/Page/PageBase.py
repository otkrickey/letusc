from dataclasses import dataclass, field

from letusc.logger import Log
from letusc.Model.BaseModel import BaseModel


@dataclass
class PageBase(BaseModel):
    __logger = Log("Model.PageBase")
    code: str  # `year:type:object_id`

    year: str = field(init=False)
    type: str = field(init=False)
    object_id: str = field(init=False)
    url: str = field(init=False)
    accounts: list[str] = field(init=False)  # `multi_id`[]

    def to_api(self) -> dict:
        return {
            "code": self.code,
            "accounts": self.accounts,
        }


__all__ = [
    "PageBase",
]
