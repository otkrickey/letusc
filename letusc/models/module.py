import re
from dataclasses import dataclass, field
from datetime import datetime

import bs4

from ..db import DBManager
from ..logger import get_logger
from .base import (
    BaseDatabase,
    BaseModel,
    BaseParser,
    attrs,
    from_api_attrs,
    to_api_attrs,
    types,
)
from .code import ContentCode, ModuleCode

logger = get_logger(__name__)

__all__ = [
    "ModuleBase",
    "Module",
    "LabelModule",
    "PageModule",
    "URLModule",
    "ResourceModule",
    "FolderModule",
    "FeedbackModule",
    "ForumModule",
    "ModuleParser",
    "NewModule",
    "NewLabelModule",
    "NewPageModule",
    "NewURLModule",
    "NewResourceModule",
    "NewFolderModule",
    "NewFeedbackModule",
    "NewForumModule",
]


@dataclass
class ModuleBase(ModuleCode, BaseDatabase, BaseModel):
    _attrs = (
        BaseModel._attrs
        | ModuleCode._attrs
        | attrs(
            [
                "title",
                "module_url",
                "main",
                "uploaded_at",
                "hash",
                "timestamp",
            ]
        )
    )
    _types = (
        BaseModel._types
        | ModuleCode._types
        | types(
            [
                ("title", "Title", str),
                ("module_url", "ModuleURL", str | None),
                ("main", "Main", str),
                ("uploaded_at", "UploadedAt", datetime | None),
                ("hash", "Hash", str),
                ("timestamp", "Timestamp", datetime),
            ]
        )
    )
    _from_api_attrs = (
        BaseModel._from_api_attrs
        | ModuleCode._from_api_attrs
        | from_api_attrs(
            [
                ("title", str, lambda obj: obj["title"]),
                ("module_url", str | None, lambda obj: obj["module_url"]),
                ("main", str, lambda obj: obj["main"]),
                ("uploaded_at", datetime | None, lambda obj: obj["uploaded_at"]),
                ("hash", str, lambda obj: obj["hash"]),
                ("timestamp", datetime, lambda obj: obj["timestamp"]),
            ]
        )
    )
    _to_api_attrs = (
        BaseModel._to_api_attrs
        | ModuleCode._to_api_attrs
        | to_api_attrs(
            [
                ("title", lambda self: self.title),
                ("module_url", lambda self: self.module_url),
                ("main", lambda self: self.main),
                ("uploaded_at", lambda self: self.uploaded_at),
                ("hash", lambda self: self.hash),
                ("timestamp", lambda self: self.timestamp),
            ]
        )
    )

    collection = DBManager.get_collection("letus", "modules")
    code: str

    title: str = field(init=False)
    module_url: str | None = field(init=False)
    main: str = field(init=False)
    uploaded_at: datetime | None = field(init=False)

    hash: str = field(init=False)
    timestamp: datetime = field(init=False)

    def __post_init__(self):
        BaseModel.__post_init__(self)
        ModuleCode.__post_init__(self)


@dataclass
class Module(ModuleBase):
    def __post_init__(self):
        ModuleBase.__post_init__(self)

    @classmethod
    async def pull(cls, code: str) -> "Module":
        _code = ModuleCode.create(code)
        match _code.module_type:
            case "label":
                module = LabelModule(code)
            case "page":
                module = PageModule(code)
            case "url":
                module = URLModule(code)
            case "resource":
                module = ResourceModule(code)
            case "folder":
                module = FolderModule(code)
            case "feedback":
                module = FeedbackModule(code)
            case "forum":
                module = ForumModule(code)
            case "assign":
                module = AssignModule(code)
            case _:
                module = cls(code)
                # NOTE: this will be removed if all module types are known.
                logger.warn(f"The module type {_code.module_type} is not implemented.")
                ## raise ValueError(logger.c("UnknownModuleType"))
        module.from_api(await module._pull())
        return module


@dataclass
class LabelModule(Module):
    _from_api_attrs = Module._from_api_attrs | from_api_attrs(
        [
            ("module_url", type(None), lambda obj: obj["module_url"]),
            ("main", str, lambda obj: obj["main"]),
            ("uploaded_at", type(None), lambda obj: obj["uploaded_at"]),
        ]
    )

    def __post_init__(self):
        Module.__post_init__(self)


@dataclass
class PageModule(Module):
    _from_api_attrs = Module._from_api_attrs | from_api_attrs(
        [
            ("module_url", str, lambda obj: obj["module_url"]),
            ("uploaded_at", type(None), lambda obj: obj["uploaded_at"]),
        ]
    )

    module_url: str = field(init=False)

    def __post_init__(self):
        Module.__post_init__(self)


@dataclass
class URLModule(Module):
    _from_api_attrs = Module._from_api_attrs | from_api_attrs(
        [
            ("module_url", str, lambda obj: obj["module_url"]),
            ("uploaded_at", type(None), lambda obj: obj["uploaded_at"]),
        ]
    )

    module_url: str = field(init=False)

    def __post_init__(self):
        Module.__post_init__(self)


@dataclass
class ResourceModule(Module):
    _from_api_attrs = Module._from_api_attrs | from_api_attrs(
        [
            ("module_url", str, lambda obj: obj["module_url"]),
            ("uploaded_at", datetime, lambda obj: obj["uploaded_at"]),
        ]
    )

    module_url: str = field(init=False)
    uploaded_at: datetime = field(init=False)

    def __post_init__(self):
        Module.__post_init__(self)


@dataclass
class FolderModule(Module):
    _from_api_attrs = Module._from_api_attrs | from_api_attrs(
        [
            ("uploaded_at", type(None), lambda obj: obj["uploaded_at"]),
        ]
    )

    def __post_init__(self):
        Module.__post_init__(self)


@dataclass
class FeedbackModule(Module):
    _from_api_attrs = Module._from_api_attrs | from_api_attrs(
        [
            ("module_url", str, lambda obj: obj["module_url"]),
            ("uploaded_at", type(None), lambda obj: obj["uploaded_at"]),
        ]
    )

    module_url: str = field(init=False)

    def __post_init__(self):
        Module.__post_init__(self)


@dataclass
class ForumModule(Module):
    _from_api_attrs = Module._from_api_attrs | from_api_attrs(
        [
            ("module_url", str, lambda obj: obj["module_url"]),
            ("uploaded_at", type(None), lambda obj: obj["uploaded_at"]),
        ]
    )

    module_url: str = field(init=False)

    def __post_init__(self):
        Module.__post_init__(self)


@dataclass
class AssignModule(Module):
    _from_api_attrs = Module._from_api_attrs | from_api_attrs(
        [
            ("module_url", str, lambda obj: obj["module_url"]),
            ("uploaded_at", type(None), lambda obj: obj["uploaded_at"]),
        ]
    )

    module_url: str = field(init=False)

    def __post_init__(self):
        Module.__post_init__(self)


@dataclass
class ModuleParser(BaseParser, ModuleBase):
    def __post_init__(self):
        ModuleBase.__post_init__(self)

    def _get_module_title(self, tag) -> str:
        if not isinstance(tag, bs4.Tag):
            return "<NoModuleTitleFound>"
        return tag.attrs["data-activityname"]

    def _get_uploaded_at(self, tag) -> datetime | None:
        if not isinstance(tag, bs4.Tag):
            return None
        text = self._tag_filter(tag)
        try:
            match = re.search(r"(\d{2}年 \d{2}月 \d{2}日 \d{2}:\d{2})", text)
            if not match:
                logger.error(f"Invalid datetime format: {text}")
                return None
            extracted_date = match.group(1)
            uploaded_at = datetime.strptime(extracted_date, "%y年 %m月 %d日 %H:%M")
        except Exception as e:
            logger.error(f"Invalid datetime format: {text}")
            logger.error(e)
            return None
        return uploaded_at

    async def _parse(self, tag: bs4.Tag) -> None:
        self.title = self._get_module_title(
            tag.find(class_="activity-item", attrs={"data-activityname": True})
        )
        self.main = self._get_main(tag.find("div", {"class": "description"}))
        self.uploaded_at = self._get_uploaded_at(
            tag.find("span", {"class": "resourcelinkdetails"})
        )
        self.hash = self._get_hash(self.main)
        self.timestamp = datetime.now()
        self.check()


@dataclass
class NewModule(ModuleParser, ModuleBase):
    def __post_init__(self):
        ModuleBase.__post_init__(self)

        self.module_url = self.url

    @classmethod
    async def parse(cls, code: ContentCode, tag) -> "NewModule":
        if not isinstance(tag, bs4.Tag):
            raise ValueError(logger.c("InvalidModuleTag"))
        _code = code.createModuleCode(tag)
        match _code.module_type:
            case "label":
                module = NewLabelModule(str(_code))
            case "page":
                module = NewPageModule(str(_code))
            case "url":
                module = NewURLModule(str(_code))
            case "resource":
                module = NewResourceModule(str(_code))
            case "folder":
                module = NewFolderModule(str(_code))
            case "feedback":
                module = NewFeedbackModule(str(_code))
            case "forum":
                module = NewForumModule(str(_code))
            case "assign":
                module = NewAssignModule(str(_code))
            case _:
                module = cls(str(_code))
                # NOTE: this will be removed if all module types are known.
                logger.warn(f"The module type {_code.module_type} is not implemented.")
                # raise ValueError(logger.c("UnknownModuleType"))
        await module._parse(tag)
        return module


@dataclass
class NewLabelModule(NewModule):
    _from_api_attrs = LabelModule._from_api_attrs

    def __post_init__(self):
        NewModule.__post_init__(self)


@dataclass
class NewPageModule(NewModule):
    _from_api_attrs = PageModule._from_api_attrs

    module_url: str = field(init=False)

    def __post_init__(self):
        NewModule.__post_init__(self)


@dataclass
class NewURLModule(NewModule):
    _from_api_attrs = URLModule._from_api_attrs

    module_url: str = field(init=False)

    def __post_init__(self):
        NewModule.__post_init__(self)


@dataclass
class NewResourceModule(NewModule):
    _from_api_attrs = ResourceModule._from_api_attrs

    module_url: str = field(init=False)
    uploaded_at: datetime = field(init=False)

    def __post_init__(self):
        NewModule.__post_init__(self)


@dataclass
class NewFolderModule(NewModule):
    _from_api_attrs = FolderModule._from_api_attrs

    def __post_init__(self):
        NewModule.__post_init__(self)


@dataclass
class NewFeedbackModule(NewModule):
    _from_api_attrs = FeedbackModule._from_api_attrs

    module_url: str = field(init=False)

    def __post_init__(self):
        NewModule.__post_init__(self)


@dataclass
class NewForumModule(NewModule):
    _from_api_attrs = ForumModule._from_api_attrs

    module_url: str = field(init=False)

    def __post_init__(self):
        NewModule.__post_init__(self)


@dataclass
class NewAssignModule(NewModule):
    _from_api_attrs = AssignModule._from_api_attrs

    module_url: str = field(init=False)

    def __post_init__(self):
        NewModule.__post_init__(self)
