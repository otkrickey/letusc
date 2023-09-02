from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

import bs4
from bs4 import BeautifulSoup
from pymongo import MongoClient

from letusc.logger import Log
from letusc.URLManager import URLManager
from letusc.util import get_split_converter, parser, strs_converter

from .base import BaseDatabase, BaseModel


@dataclass
class PageBase(BaseModel):
    _logger = Log("Model.PageBase")
    code: str  # `year:page_type:page_id`

    year: str = field(init=False)
    page_type: str = field(init=False)
    page_id: str = field(init=False)
    url: str = field(init=False)

    # `multi_id`[]
    accounts: list[str] = field(default_factory=list, init=False)

    title: str = field(init=False)
    # `content_type:content_id:content_hash`[]
    contents: list[str] = field(default_factory=list, init=False)

    hash: str = field(init=False)
    timestamp: datetime = field(init=False)

    def identify(self) -> None:
        self.key_name = "code"
        self.key = self.code

    def from_api(
        self, object: dict, attrs: list[tuple[str, type, Callable]] = []
    ) -> None:
        single, multi, clear = get_split_converter(self.code, 3)
        attrs[:0] = [
            ("year", str, lambda obj: single(obj["code"], 0)),
            ("page_type", str, lambda obj: single(obj["code"], 1)),
            ("page_id", str, lambda obj: single(obj["code"], 2)),
            ("url", str, lambda obj: URLManager.getPage(*multi(obj["code"], 0, 1, 2))),
            ("accounts", list, lambda obj: strs_converter(obj["accounts"])),
            ("title", str, lambda obj: obj["title"]),
            ("contents", list, lambda obj: strs_converter(obj["contents"])),
            ("hash", str, lambda obj: obj["hash"]),
            ("timestamp", datetime, lambda obj: obj["timestamp"]),
        ]
        super().from_api(object, attrs=attrs)
        clear(self.code)
        return

    def to_api(self) -> dict:
        return {
            "code": self.code,
            "accounts": self.accounts,
            "title": self.title,
            "contents": self.contents,
            "hash": self.hash,
            "timestamp": self.timestamp,
        }


@dataclass
class PageDatabase(BaseDatabase, PageBase):
    _logger = Log("Model.Page.Database")
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


@dataclass
class Page(PageDatabase, PageBase):
    _logger = Log("Model.Page")

    def ___post_init___(self):
        self.identify()
        object = self.pull()
        self.from_api(object)

    @classmethod
    def from_code(cls, code: str) -> "Page":
        _logger = Log(f"{cls._logger}.from_code")
        try:
            code_split = code.split(":")
            if len(code_split) != 3:
                raise ValueError
        except Exception as e:
            raise ValueError(f"{_logger}:InvalidData") from e
        else:
            match code_split[1]:
                case "course":
                    return CoursePage(code)
                case _:
                    raise ValueError(f"{_logger}:UnknownType")


@dataclass
class CoursePage(Page):
    _logger = Log("Model.CoursePage")

    def __post_init__(self):
        super().___post_init___()


@dataclass
class NewPage(Page):
    _logger = Log("Model.Page.NewPage")

    def __post_init__(self):
        self.identify()
        try:
            code_split = self.code.split(":")
            if len(code_split) != 3:
                raise ValueError
        except Exception as e:
            raise ValueError("Model.Page.from_api:InvalidData") from e
        else:
            self.year = code_split[0]
            self.page_type = code_split[1]
            self.page_id = code_split[2]
            self.url = URLManager.getPage(self.year, self.page_type, self.page_id)

            self.accounts = []
            self.contents = []

    @classmethod
    def from_code(cls, code: str) -> "NewPage":
        try:
            code_split = code.split(":")
            if len(code_split) != 3:
                raise ValueError
        except Exception as e:
            raise ValueError("Model.Page.from_api:InvalidData") from e
        else:
            match code_split[1]:
                case "course":
                    return NewCoursePage(code)
                case _:
                    raise ValueError("Model.Page.from_api:UnknownType")

    def parse(self, soup: BeautifulSoup):
        title_el = soup.find(attrs={"class": "page-header-headings"})
        title = title_el.text if title_el else "<Error:NoTitleFound>"
        title = title.lstrip().rstrip()

        main = soup.find("section", {"id": "region-main"})
        if not isinstance(main, bs4.Tag):
            raise ValueError("Model.Page.parse:MainSectionNotFound")
        hash = parser.hash(parser.text_filter(str(main)))

        self.title = title
        self.hash = hash
        self.timestamp = datetime.now()

        self.check()


@dataclass
class NewCoursePage(NewPage):
    _logger = Log("Model.CoursePage")


__all__ = [
    "PageBase",
    "PageDatabase",
    "Page",
    "CoursePage",
    "NewPage",
    "NewCoursePage",
]
