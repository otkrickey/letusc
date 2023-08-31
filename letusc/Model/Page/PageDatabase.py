from dataclasses import dataclass
from datetime import datetime

from pymongo import MongoClient

from letusc.logger import Log
from letusc.Model.BaseDatabase import BaseDatabase
from letusc.URLManager import URLManager

from .PageBase import PageBase


@dataclass
class PageDatabase(BaseDatabase, PageBase):
    __logger = Log("Model.Page.Database")
    collection = MongoClient(URLManager.getMongo())["letus"]["pagesV2"]

    def check(
        self, attrs: list[str] = [], types: list[tuple[str, str, type]] = []
    ) -> None:
        attrs[:0] = ["code", "accounts", "title", "contents", "hash", "timestamp"]
        types[:0] = [
            ("Code", "code", str),
            ("Accounts", "accounts", list),
            ("Title", "title", str),
            ("Contents", "contents", list),
            ("Hash", "hash", str),
            ("Timestamp", "timestamp", datetime),
        ]
        super().check(attrs=attrs, types=types)
