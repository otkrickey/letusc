from dataclasses import dataclass
from datetime import datetime

from pymongo import MongoClient

from letusc.logger import Log
from letusc.Model.BaseDatabase import BaseDatabase
from letusc.URLManager import URLManager

from .ModuleBase import ModuleBase


@dataclass
class ModuleDatabase(BaseDatabase, ModuleBase):
    __logger = Log("Model.Module.Database")
    collection = MongoClient(URLManager.getMongo())["letus"]["modules"]

    def check(
        self, attrs: list[str] = [], types: list[tuple[str, str, type]] = []
    ) -> None:
        attrs[:0] = ["code", "title", "hash", "timestamp"]
        types[:0] = [
            ("Code", "code", str),
            ("Title", "title", str),
            ("Hash", "hash", str),
            ("Timestamp", "timestamp", datetime),
        ]
        super().check(attrs=attrs, types=types)
