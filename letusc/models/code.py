import re
from dataclasses import dataclass, field

import bs4

from ..logger import get_logger
from ..url import URLManager
from .base import BaseModel, attrs, from_api_attrs, to_api_attrs, types

logger = get_logger(__name__)

__all__ = [
    "Code",
    "PageCode",
    "ContentCode",
    "ModuleCode",
]

hash_code_eq_ = tuple[bool, bool]


@dataclass
class Code(BaseModel):
    _attrs = BaseModel._attrs | attrs(["code", "split", "url", "year"])
    _types = BaseModel._types | types(
        [
            ("code", "Code", str),
            ("split", "Split", list),
            ("url", "URL", str),
            ("year", "Year", str),
        ]
    )
    _from_api_attrs = BaseModel._from_api_attrs | from_api_attrs(
        [("code", str, lambda obj: obj["code"])]
    )
    _to_api_attrs = BaseModel._to_api_attrs | to_api_attrs(
        [("code", lambda self: self.code)]
    )

    code: str
    split: list[str] = field(init=False)
    url: str = field(init=False)
    year: str = field(init=False)

    def __post_init__(self):
        BaseModel.__post_init__(self)
        self.split = self.code.split(":")
        self.key_name = "code"
        self.key = self.code

    @classmethod
    def create(cls, code: str) -> "Code":
        split = code.split(":")
        match len(split):
            case 3:
                return PageCode(code)
            case 4:
                return PageHashCode(code)
            case 5:
                return ContentCode(code)
            case 6:
                return ContentHashCode(code)
            case 7:
                return ModuleCode(code)
            case 8:
                return ModuleHashCode(code)
            case _:
                raise ValueError(logger.c("InvalidCode"))

    def __str__(self) -> str:
        return self.code


class HashCode(Code):
    _attrs = Code._attrs | attrs(["hash"])
    _types = Code._types | types([("hash", "Hash", str)])

    hash: str = field(init=False)

    def __post_init__(self):
        Code.__post_init__(self)
        self.hash = self.split.pop()
        self.code = ":".join(self.split)

    def __str__(self) -> str:
        return f"{self.code}:{self.hash}"


@dataclass
class PageCode(Code):
    _attrs = Code._attrs | attrs(["page_type", "page_id"])
    _types = Code._types | types(
        [
            ("page_type", "PageType", str),
            ("page_id", "PageID", str),
        ]
    )

    page_type: str = field(init=False)
    page_id: str = field(init=False)

    def __post_init__(self):
        Code.__post_init__(self)
        self.year = self.split[0]
        self.page_type = self.split[1]
        self.page_id = self.split[2]
        self.url = URLManager.getPage(self.year, self.page_type, self.page_id)

    @classmethod
    def create(cls, code: str) -> "PageCode":
        _code = Code.create(code)
        if not isinstance(_code, PageCode):
            raise ValueError(logger.c("InvalidCode"))
        return _code

    def createContentCode(self, tag) -> "ContentCode":
        if not isinstance(tag, bs4.Tag):
            raise ValueError(logger.c("NoContentTypeFound"))
        content_type = tag.attrs["data-for"]
        content_id = tag.attrs["data-id"]
        return ContentCode.create(f"{self.code}:{content_type}:{content_id}")


@dataclass
class PageHashCode(PageCode, HashCode):
    _attrs = PageCode._attrs | HashCode._attrs
    _types = PageCode._types | HashCode._types

    def __post_init__(self):
        PageCode.__post_init__(self)
        HashCode.__post_init__(self)

    @classmethod
    def create(cls, code: str) -> "PageHashCode":
        _code = Code.create(code)
        if not isinstance(_code, PageHashCode):
            raise ValueError(logger.c("InvalidCode"))
        return _code


@dataclass
class ContentCode(PageCode):
    _attrs = PageCode._attrs | attrs(["content_type", "content_id"])
    _types = PageCode._types | types(
        [
            ("content_type", "ContentType", str),
            ("content_id", "ContentID", str),
        ]
    )

    content_type: str = field(init=False)
    content_id: str = field(init=False)

    def __post_init__(self):
        PageCode.__post_init__(self)
        self.content_type = self.split[3]
        self.content_id = self.split[4]
        self.url = URLManager.getPage(self.year, self.page_type, self.page_id)

    @classmethod
    def create(cls, code: str) -> "ContentCode":
        _code = Code.create(code)
        if not isinstance(_code, ContentCode):
            raise ValueError(logger.c("InvalidCode"))
        return _code

    def createContentCode(self, tag):
        raise NotImplementedError(logger.c("NotImplemented"))

    def createModuleCode(self, tag) -> "ModuleCode":
        if not isinstance(tag, bs4.Tag):
            raise ValueError(logger.c("NoModuleTypeFound"))
        match = re.search(r"modtype_([a-z]+)", ",".join(tag.attrs["class"]))
        if not match:
            raise ValueError(logger.c("NoModuleTypeFound"))
        module_type = match.group(1)
        module_id = tag.attrs["data-id"]
        return ModuleCode.create(f"{self.code}:{module_type}:{module_id}")


@dataclass
class ContentHashCode(ContentCode, HashCode):
    _attrs = ContentCode._attrs | HashCode._attrs
    _types = ContentCode._types | HashCode._types

    def __post_init__(self):
        ContentCode.__post_init__(self)
        HashCode.__post_init__(self)

    @classmethod
    def create(cls, code: str) -> "ContentHashCode":
        _code = Code.create(code)
        if not isinstance(_code, ContentHashCode):
            raise ValueError(logger.c("InvalidCode"))
        return _code


@dataclass
class ModuleCode(ContentCode):
    _attrs = ContentCode._attrs | attrs(["module_type", "module_id"])
    _types = ContentCode._types | types(
        [
            ("module_type", "ModuleType", str),
            ("module_id", "ModuleID", str),
        ]
    )

    module_type: str = field(init=False)
    module_id: str = field(init=False)

    def __post_init__(self):
        ContentCode.__post_init__(self)
        self.module_type = self.split[5]
        self.module_id = self.split[6]
        self.url = URLManager.getModule(self.year, self.module_type, self.module_id)

    @classmethod
    def create(cls, code: str) -> "ModuleCode":
        _code = Code.create(code)
        if not isinstance(_code, ModuleCode):
            raise ValueError(logger.c("InvalidCode"))
        return _code

    def createModuleCode(self, tag):
        raise NotImplementedError(logger.c("NotImplemented"))


@dataclass
class ModuleHashCode(ModuleCode, HashCode):
    _attrs = ModuleCode._attrs | HashCode._attrs
    _types = ModuleCode._types | HashCode._types

    def __post_init__(self):
        ModuleCode.__post_init__(self)
        HashCode.__post_init__(self)

    @classmethod
    def create(cls, code: str) -> "ModuleHashCode":
        _code = Code.create(code)
        if not isinstance(_code, ModuleHashCode):
            raise ValueError(logger.c("InvalidCode"))
        return _code
