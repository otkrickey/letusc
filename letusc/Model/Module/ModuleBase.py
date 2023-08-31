from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

from letusc.logger import Log
from letusc.Model.BaseModel import BaseModel
from letusc.URLManager import URLManager
from letusc.util import get_split_converter, strs_converter


@dataclass
class ModuleBase(BaseModel):
    __logger = Log("Model.ModuleBase")
    code: str  # `year:page_type:page_id:content_type:content_id:module_type:module_id`

    year: str = field(init=False)
    page_type: str = field(init=False)
    page_id: str = field(init=False)
    content_type: str = field(init=False)
    content_id: str = field(init=False)
    module_type: str = field(init=False)
    module_id: str = field(init=False)
    url: str = field(init=False)

    title: str | None = field(init=False)
    module_url: str | None = field(init=False)
    main: str | None = field(init=False)
    uploaded_at: datetime | None = field(init=False)

    hash: str = field(init=False)
    timestamp: datetime = field(init=False)

    def identify(self) -> None:
        self.key_name = "code"
        self.key = self.code

    def from_api(
        self, object: dict, attrs: list[tuple[str, type, Callable]] = []
    ) -> None:
        single, multi, clear = get_split_converter(self.code, 7)
        attrs[:0] = [
            ("year", str, lambda obj: single(obj["code"], 0)),
            ("page_type", str, lambda obj: single(obj["code"], 1)),
            ("page_id", str, lambda obj: single(obj["code"], 2)),
            ("content_type", str, lambda obj: single(obj["code"], 3)),
            ("content_id", str, lambda obj: single(obj["code"], 4)),
            ("module_type", str, lambda obj: single(obj["code"], 5)),
            ("module_id", str, lambda obj: single(obj["code"], 6)),
            ("url", str, lambda obj: URLManager.getPage(*multi(obj["code"], 0, 1, 2))),
            ("title", str, lambda obj: obj["title"]),
            ("module_url", str | None, lambda obj: obj["module_url"]),
            ("main", str | None, lambda obj: obj["main"]),
            ("uploaded_at", datetime | None, lambda obj: obj["uploaded_at"]),
            ("hash", str, lambda obj: obj["hash"]),
            ("timestamp", datetime, lambda obj: obj["timestamp"]),
        ]
        super().from_api(object, attrs=attrs)
        clear(self.code)
        return

    def to_api(self) -> dict:
        return {
            "code": self.code,
            "title": self.title,
            "module_url": self.module_url,
            "main": self.main,
            "uploaded_at": self.uploaded_at,
            "hash": self.hash,
            "timestamp": self.timestamp,
        }
