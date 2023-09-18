from dataclasses import dataclass, field
from datetime import datetime

import bs4

from letusc.logger import L
from letusc.MongoManager import MongoManager

from .base import (
    BaseDatabase,
    BaseModel,
    BaseParser,
    attrs,
    from_api_attrs,
    to_api_attrs,
    types,
)
from .code import ContentCode, ContentHashCode, ModuleHashCode, PageCode
from .module import NewModule

__all__ = [
    "ContentBase",
    "Content",
    "SectionContent",
    "ContentParser",
    "NewContent",
    "NewSectionContent",
]


@dataclass
class ContentBase(ContentCode, BaseDatabase, BaseModel):
    _l = L()
    _attrs = (
        BaseModel._attrs
        | ContentCode._attrs
        | attrs(
            [
                "title",
                "main",
                "modules",
                "hash",
                "timestamp",
            ]
        )
    )
    _types = (
        BaseModel._types
        | ContentCode._types
        | types(
            [
                ("title", "Title", str),
                ("main", "Main", str),
                ("modules", "Modules", list),
                ("hash", "Hash", str),
                ("timestamp", "Timestamp", datetime),
            ]
        )
    )
    _from_api_attrs = (
        BaseModel._from_api_attrs
        | ContentCode._from_api_attrs
        | from_api_attrs(
            [
                ("title", str, lambda obj: obj["title"]),
                ("main", str, lambda obj: obj["main"]),
                # ("modules", list, lambda obj: strs2list(obj["modules"])),
                (
                    "modules",
                    dict[str, ModuleHashCode],
                    lambda obj: {
                        m.code: m
                        for m in [
                            ModuleHashCode.create(f"{k}:{v}")
                            for k, v in obj["modules"].items()
                        ]
                    },
                ),
                ("hash", str, lambda obj: obj["hash"]),
                ("timestamp", datetime, lambda obj: obj["timestamp"]),
            ]
        )
    )
    _to_api_attrs = (
        BaseModel._to_api_attrs
        | ContentCode._to_api_attrs
        | to_api_attrs(
            [
                ("title", lambda self: self.title),
                ("main", lambda self: self.main),
                ("modules", lambda self: {k: v.hash for k, v in self.modules.items()}),
                ("hash", lambda self: self.hash),
                ("timestamp", lambda self: self.timestamp),
            ]
        )
    )

    collection = MongoManager.get_collection("letus", "contents")
    code: str

    title: str = field(init=False)
    main: str = field(init=False)
    modules: dict[str, ModuleHashCode] = field(init=False, default_factory=dict)
    hash: str = field(init=False)
    timestamp: datetime = field(init=False)

    def __post_init__(self):
        BaseModel.__post_init__(self)
        ContentCode.__post_init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")


@dataclass
class Content(ContentBase):
    _l = L()

    def __post_init__(self):
        ContentBase.__post_init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")

    @classmethod
    async def pull(cls, code: str) -> "Content":
        _l = L(cls.__name__).gm("pull")
        _code = ContentCode.create(code)
        match _code.content_type:
            case "section":
                content = SectionContent(code=code)
            case _:
                raise ValueError(_l.c("UnknownContentType"))
        content.from_api(await content._pull())
        return content


@dataclass
class SectionContent(Content):
    _l = L()

    def __post_init__(self):
        Content.__post_init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")


@dataclass
class ContentParser(BaseParser, ContentBase):
    _l = L()

    # modules: list[NewModule] = field(init=False, default_factory=list)
    modules: dict[str, NewModule] = field(init=False, default_factory=dict)

    async def _parse(self, tag: bs4.Tag) -> None:
        _l = self._l.gm("_parse")
        self.title = self._get_title(
            tag.find("h3", attrs={"data-for": "section_title"})
        )
        self.main = self._get_main(tag.find("div", {"class": "summarytext"}))
        self.modules = {
            m.code: m
            for m in [
                await NewModule.parse(self, module_el)
                for module_el in tag.find_all(attrs={"data-for": "cmitem"})
            ]
        }
        self.hash = self._get_hash(tag)
        self.timestamp = datetime.now()
        self.check()


@dataclass
class NewContent(ContentParser, ContentHashCode, ContentBase):
    _l = L()

    def __post_init__(self):
        ContentBase.__post_init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")

    @classmethod
    async def parse(cls, code: PageCode, tag) -> "NewContent":
        _l = L(cls.__name__).gm("parse")
        if not isinstance(tag, bs4.Tag):
            raise ValueError(_l.c("InvalidContentTag"))
        _code = code.createContentCode(tag)
        match _code.content_type:
            case "section":
                content = NewSectionContent(str(_code))
            case _:
                raise ValueError(_l.c("UnknownContentType"))
        await content._parse(tag)
        return content


@dataclass
class NewSectionContent(NewContent):
    _l = L()

    def __post_init__(self):
        NewContent.__post_init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")
