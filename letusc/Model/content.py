from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

import bs4
from pymongo import MongoClient

from letusc.logger import Log
from letusc.URLManager import URLManager
from letusc.util import get_split_converter, parser, strs_converter

from .base import BaseDatabase, BaseModel


@dataclass
class ContentBase(BaseModel):
    __logger = Log("Model.ContentBase")
    code: str  # `year:page_type:page_id:content_type:content_id`

    year: str = field(init=False)
    page_type: str = field(init=False)
    page_id: str = field(init=False)
    content_type: str = field(init=False)
    content_id: str = field(init=False)
    url: str = field(init=False)

    title: str = field(init=False)
    main: str = field(init=False)
    modules: list[str] = field(init=False)  # `module_type:module_id:module_hash`[]

    hash: str = field(init=False)
    timestamp: datetime = field(init=False)

    def identify(self) -> None:
        self.key_name = "code"
        self.key = self.code

    def from_api(
        self, object: dict, attrs: list[tuple[str, type, Callable]] = []
    ) -> None:
        single, multi, clear = get_split_converter(self.code, 5)
        attrs[:0] = [
            ("year", str, lambda obj: single(obj["code"], 0)),
            ("page_type", str, lambda obj: single(obj["code"], 1)),
            ("page_id", str, lambda obj: single(obj["code"], 2)),
            ("content_type", str, lambda obj: single(obj["code"], 3)),
            ("content_id", str, lambda obj: single(obj["code"], 4)),
            ("url", str, lambda obj: URLManager.getPage(*multi(obj["code"], 0, 1, 2))),
            ("title", str, lambda obj: obj["title"]),
            ("main", str, lambda obj: obj["main"]),
            ("modules", list, lambda obj: strs_converter(obj["modules"])),
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
            "main": self.main,
            "modules": self.modules,
            "hash": self.hash,
            "timestamp": self.timestamp,
        }


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


@dataclass
class Content(ContentDatabase, ContentBase):
    __logger = Log("Model.Content")

    def ___post_init___(self):
        self.identify()
        object = self.pull()
        self.from_api(object)

    @classmethod
    def from_code(cls, code: str) -> "SectionContent":
        __logger = Log(f"{cls.__logger}.from_code")
        try:
            code_split = code.split(":")
            if len(code_split) != 5:
                raise ValueError
        except Exception as e:
            raise ValueError(f"{__logger}:InvalidData") from e
        else:
            match code_split[3]:
                case "section":
                    return SectionContent(code)
                case _:
                    raise ValueError(f"{__logger}:UnknownType")


@dataclass
class SectionContent(Content):
    __logger = Log("Model.Content.SectionContent")

    def __post_init__(self):
        super().___post_init___()


@dataclass
class NewContent(Content):
    __logger = Log("Model.Content.NewContent")

    # title: str
    # main: str

    # hash: str
    # timestamp: datetime

    def __post_init__(self):
        self.identify()
        try:
            code_split = self.code.split(":")
            if len(code_split) != 5:
                raise ValueError
        except Exception as e:
            raise ValueError(f"{self.__logger}:InvalidData") from e
        else:
            self.year = code_split[0]
            self.page_type = code_split[1]
            self.page_id = code_split[2]
            self.content_type = code_split[3]
            self.content_id = code_split[4]
            self.url = URLManager.getPage(self.year, self.page_type, self.page_id)

            self.modules = []

    @classmethod
    def from_code(cls, code: str) -> "NewContent":
        __logger = Log(f"{cls.__logger}.from_code")
        try:
            code_split = code.split(":")
            if len(code_split) != 5:
                raise ValueError
        except Exception as e:
            raise ValueError(f"{__logger}:InvalidData") from e
        else:
            match code_split[3]:
                case "section":
                    return NewSectionContent(code)
                case _:
                    raise ValueError(f"{__logger}:UnknownType")

    def parse(self, el: bs4.Tag):
        title_el = el.find("h3", attrs={"data-for": "section_title"})
        if not isinstance(title_el, bs4.Tag):
            raise Exception("PageParser.get_content:TitleIsNotTag")
        title = title_el.text.lstrip().rstrip()

        main_el = el.find("div", {"class": "summarytext"})
        if not isinstance(main_el, bs4.Tag):
            main = ""
        else:
            for br in main_el.find_all("br"):
                br.replace_with("\n")
            tags = ["div", "span"]
            for tag in tags:
                for child in main_el.find_all(tag):
                    child.replace_with(child.text)
            main = "\n".join(main_el.stripped_strings)

        hash = parser.hash(parser.text_filter(str(el)))

        self.title = title
        self.main = main
        self.hash = hash
        self.timestamp = datetime.now()

        self.check()


@dataclass
class NewSectionContent(NewContent):
    __logger = Log("Model.Content.NewSectionContent")


__all__ = [
    "ContentBase",
    "ContentDatabase",
    "Content",
    "SectionContent",
    "NewContent",
    "NewSectionContent",
]
