from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

import bs4
from pymongo import MongoClient

from letusc.logger import Log
from letusc.URLManager import URLManager
from letusc.util import get_split_converter, parser

from .base import BaseDatabase, BaseModel


@dataclass
class ModuleBase(BaseModel):
    _logger = Log("Model.ModuleBase")
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


@dataclass
class ModuleDatabase(BaseDatabase, ModuleBase):
    _logger = Log("Model.Module.Database")
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


@dataclass
class Module(ModuleDatabase, ModuleBase):
    _logger = Log("Model.Module")

    def ___post_init___(self):
        self.identify()
        object = self.pull()
        self.from_api(object)

    @classmethod
    def from_code(cls, code: str) -> "Module":
        _logger = Log(f"{cls._logger}.from_code")
        try:
            code_split = code.split(":")
            if len(code_split) != 7:
                raise ValueError
        except Exception as e:
            raise ValueError(f"{_logger}:InvalidData") from e
        else:
            match code_split[5]:
                case "label":
                    return LabelModule(code)
                case "page":
                    return PageModule(code)
                case "url":
                    return URLModule(code)
                case "resource":
                    return ResourceModule(code)
                case "folder":
                    return FolderModule(code)
                case "feedback":
                    return FeedbackModule(code)
                case _:
                    raise ValueError(f"{_logger}:UnknownType")


@dataclass
class LabelModule(Module):
    _logger = Log("Model.Module.LabelModule")

    main: str = field(init=False)

    def __post_init__(self):
        self.identify()
        object = self.pull()
        try:
            main = object["main"]
            if not isinstance(main, str):
                raise ValueError
        except Exception as e:
            raise ValueError(f"{LabelModule._logger}:InvalidData") from e
        self.from_api(object)


@dataclass
class PageModule(Module):
    _logger = Log("Model.Module.PageModule")

    title: str = field(init=False)
    module_url: str = field(init=False)

    def __post_init__(self):
        self.identify()
        object = self.pull()
        try:
            title = object["title"]
            module_url = object["module_url"]
            if not isinstance(title, str):
                raise ValueError
            if not isinstance(module_url, str):
                raise ValueError
        except Exception as e:
            raise ValueError(f"{PageModule._logger}:InvalidData") from e
        self.from_api(object)


@dataclass
class URLModule(Module):
    _logger = Log("Model.Module.URLModule")

    title: str = field(init=False)
    module_url: str = field(init=False)

    def __post_init__(self):
        self.identify()
        object = self.pull()
        try:
            title = object["title"]
            module_url = object["module_url"]
            if not isinstance(title, str):
                raise ValueError
            if not isinstance(module_url, str):
                raise ValueError
        except Exception as e:
            raise ValueError(f"{URLModule._logger}:InvalidData") from e
        self.from_api(object)


@dataclass
class ResourceModule(Module):
    _logger = Log("Model.Module.ResourceModule")

    title: str = field(init=False)
    module_url: str = field(init=False)
    uploaded_at: str = field(init=False)

    def __post_init__(self):
        self.identify()
        object = self.pull()
        try:
            title = object["title"]
            module_url = object["module_url"]
            uploaded_at = object["uploaded_at"]
            if not isinstance(title, str):
                raise ValueError
            if not isinstance(module_url, str):
                raise ValueError
            if not isinstance(uploaded_at, str):
                raise ValueError
        except Exception as e:
            raise ValueError(f"{ResourceModule._logger}:InvalidData") from e
        self.from_api(object)


@dataclass
class FolderModule(Module):
    _logger = Log("Model.Module.FolderModule")

    title: str = field(init=False)

    def __post_init__(self):
        self.identify()
        object = self.pull()
        try:
            title = object["title"]
            if not isinstance(title, str):
                raise ValueError
        except Exception as e:
            raise ValueError(f"{FolderModule._logger}:InvalidData") from e
        self.from_api(object)


@dataclass
class FeedbackModule(Module):
    _logger = Log("Model.Module.FeedbackModule")

    title: str = field(init=False)
    module_url: str = field(init=False)
    uploaded_at: str = field(init=False)

    def __post_init__(self):
        self.identify()
        object = self.pull()
        try:
            title = object["title"]
            module_url = object["module_url"]
            # uploaded_at = object["uploaded_at"]
            if not isinstance(title, str):
                raise ValueError
            if not isinstance(module_url, str):
                raise ValueError
            # if not isinstance(uploaded_at, str):
            #     raise ValueError
        except Exception as e:
            raise ValueError(f"{FeedbackModule._logger}:InvalidData") from e
        self.from_api(object)


@dataclass
class NewModule(Module):
    _logger = Log("Model.Module.NewModule")

    def __post_init__(self):
        self.identify()
        try:
            code_split = self.code.split(":")
            if len(code_split) != 7:
                raise ValueError
        except Exception as e:
            raise ValueError(f"{NewModule._logger}:InvalidData") from e
        else:
            self.year = code_split[0]
            self.page_type = code_split[1]
            self.page_id = code_split[2]
            self.content_type = code_split[3]
            self.content_id = code_split[4]
            self.module_type = code_split[5]
            self.module_id = code_split[6]
            self.url = URLManager.getPage(self.year, self.page_type, self.page_id)

    @classmethod
    def from_code(cls, code: str) -> "NewModule":
        _logger = Log(f"{NewModule._logger}.from_code")
        try:
            code_split = code.split(":")
            if len(code_split) != 7:
                raise ValueError
        except Exception as e:
            raise ValueError(f"{_logger}:InvalidData") from e
        else:
            match code_split[5]:
                case "label":
                    return NewLabelModule(code)
                case "page":
                    return NewPageModule(code)
                case "url":
                    return NewURLModule(code)
                case "resource":
                    return NewResourceModule(code)
                case "folder":
                    return NewFolderModule(code)
                case "feedback":
                    return NewFeedbackModule(code)
                case _:
                    _logger.error(f"Unknown module type: {code_split[5]}")
                    return NewModule(code)

    def parse(self, el: bs4.Tag):
        title_el = el.find(class_="activity-item", attrs={"data-activityname": True})
        title = (
            title_el.attrs["data-activityname"]
            if isinstance(title_el, bs4.Tag)
            else "<Error:NoTitleFound>"
        )

        module_url = URLManager.getModuleByCode(self.code)

        main_el = el.find("div", {"class": "description"})
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

        uploaded_at_el = el.find("span", {"class": "resourcelinkdetails"})
        uploaded_at_str = parser.tag_filter(uploaded_at_el)
        uploaded_at = None
        if isinstance(uploaded_at_str, str):
            uploaded_at = datetime.strptime(uploaded_at_str, "アップロード %y年 %m月 %d日 %H:%M")

        hash = parser.hash(main)

        self.title = title
        self.module_url = module_url
        self.main = main
        self.uploaded_at = uploaded_at
        self.hash = hash
        self.timestamp = datetime.now()

        self.check()


@dataclass
class NewLabelModule(NewModule):
    _logger = Log("Model.Module.NewLabelModule")

    main: str = field(init=False)

    def parse(self, el: bs4.Tag):
        super().parse(el)
        self.module_url = None


@dataclass
class NewPageModule(NewModule):
    _logger = Log("Model.Module.NewPageModule")

    title: str = field(init=False)
    module_url: str = field(init=False)


@dataclass
class NewURLModule(NewModule):
    _logger = Log("Model.Module.NewURLModule")

    title: str = field(init=False)
    module_url: str = field(init=False)


@dataclass
class NewResourceModule(NewModule):
    _logger = Log("Model.Module.NewResourceModule")

    title: str = field(init=False)
    module_url: str = field(init=False)
    uploaded_at: datetime = field(init=False)


@dataclass
class NewFolderModule(NewModule):
    _logger = Log("Model.Module.NewFolderModule")

    title: str = field(init=False)


@dataclass
class NewFeedbackModule(NewModule):
    _logger = Log("Model.Module.NewFeedbackModule")

    title: str = field(init=False)
    module_url: str = field(init=False)


__all__ = [
    "ModuleBase",
    "ModuleDatabase",
    "Module",
    "LabelModule",
    "PageModule",
    "URLModule",
    "ResourceModule",
    "FolderModule",
    "FeedbackModule",
    "NewModule",
    "NewLabelModule",
    "NewPageModule",
    "NewURLModule",
    "NewResourceModule",
    "NewFolderModule",
    "NewFeedbackModule",
]
