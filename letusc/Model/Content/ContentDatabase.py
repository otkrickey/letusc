from dataclasses import dataclass
from datetime import datetime

from pymongo import MongoClient

from letusc.logger import Log
from letusc.Model.BaseDatabase import BaseDatabase
from letusc.URLManager import URLManager

from .ContentBase import ContentBase


@dataclass
class ContentDatabase(BaseDatabase, ContentBase):
    __logger = Log("Model.Content.Database")
    collection = MongoClient(URLManager.getMongo())["letus"]["contents"]

    def check(
        self, attrs: list[str] = [], types: list[tuple[str, str, type]] = []
    ) -> None:
        attrs[:0] = ["code", "title", "main", "modules", "hash", "timestamp"]
        types[:0] = [
            ("Code", "code", str),
            ("Title", "title", str),
            ("Main", "main", str),
            ("Modules", "modules", list),
            ("Hash", "hash", str),
            ("Timestamp", "timestamp", datetime),
        ]
        super().check(attrs=attrs, types=types)
