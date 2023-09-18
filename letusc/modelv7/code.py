import code
import re
from dataclasses import dataclass, field

import bs4

from letusc.logger import L
from letusc.URLManager import URLManager

from .base import BaseModel, attrs, from_api_attrs, to_api_attrs, types

__all__ = [
    "Code",
    "PageCode",
    "ContentCode",
    "ModuleCode",
]

# hash_code_eq_ = bool | tuple[bool, bool]
hash_code_eq_ = tuple[bool, bool]


@dataclass
class Code(BaseModel):
    _l = L()
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
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")
        self.split = self.code.split(":")
        self.key_name = "code"
        self.key = self.code

    @classmethod
    def create(cls, code: str) -> "Code":
        _l = L(cls.__name__).gm("create")
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
                raise ValueError(_l.c("InvalidCode"))

    def __str__(self) -> str:
        return self.code


class HashCode(Code):
    _l = L()
    _attrs = Code._attrs | attrs(["hash"])
    _types = Code._types | types([("hash", "Hash", str)])

    hash: str = field(init=False)

    def __post_init__(self):
        Code.__post_init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")
        self.hash = self.split.pop()
        self.code = ":".join(self.split)

    def __str__(self) -> str:
        return f"{self.code}:{self.hash}"


@dataclass
class PageCode(Code):
    _l = L()
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
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")
        self.year = self.split[0]
        self.page_type = self.split[1]
        self.page_id = self.split[2]
        self.url = URLManager.getPage(self.year, self.page_type, self.page_id)

    @classmethod
    def create(cls, code: str) -> "PageCode":
        _l = L(cls.__name__).gm("create")
        _code = Code.create(code)
        if not isinstance(_code, PageCode):
            raise ValueError(_l.c("InvalidCode"))
        return _code

    def createContentCode(self, tag) -> "ContentCode":
        _l = self._l.gm("createContentCode")
        if not isinstance(tag, bs4.Tag):
            raise ValueError(_l.c("NoContentTypeFound"))
        content_type = tag.attrs["data-for"]
        content_id = tag.attrs["data-id"]
        return ContentCode.create(f"{self.code}:{content_type}:{content_id}")


@dataclass
class PageHashCode(PageCode, HashCode):
    _l = L()
    _attrs = PageCode._attrs | HashCode._attrs
    _types = PageCode._types | HashCode._types

    def __post_init__(self):
        PageCode.__post_init__(self)
        HashCode.__post_init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")

    @classmethod
    def create(cls, code: str) -> "PageHashCode":
        _l = L(cls.__name__).gm("create")
        _code = Code.create(code)
        if not isinstance(_code, PageHashCode):
            raise ValueError(_l.c("InvalidCode"))
        return _code


@dataclass
class ContentCode(PageCode):
    _l = L()
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
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")
        self.content_type = self.split[3]
        self.content_id = self.split[4]
        self.url = URLManager.getPage(self.year, self.page_type, self.page_id)

    @classmethod
    def create(cls, code: str) -> "ContentCode":
        _l = L(cls.__name__).gm("create")
        _code = Code.create(code)
        if not isinstance(_code, ContentCode):
            raise ValueError(_l.c("InvalidCode"))
        return _code

    def createContentCode(self, tag):
        raise NotImplementedError(self._l.c("NotImplemented"))

    def createModuleCode(self, tag) -> "ModuleCode":
        _l = self._l.gm("createModuleCode")
        if not isinstance(tag, bs4.Tag):
            raise ValueError(_l.c("NoModuleTypeFound"))
        match = re.search(r"modtype_([a-z]+)", ",".join(tag.attrs["class"]))
        if not match:
            raise ValueError(_l.c("NoModuleTypeFound"))
        module_type = match.group(1)
        module_id = tag.attrs["data-id"]
        return ModuleCode.create(f"{self.code}:{module_type}:{module_id}")


@dataclass
class ContentHashCode(ContentCode, HashCode):
    _l = L()
    _attrs = ContentCode._attrs | HashCode._attrs
    _types = ContentCode._types | HashCode._types

    def __post_init__(self):
        ContentCode.__post_init__(self)
        HashCode.__post_init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")

    @classmethod
    def create(cls, code: str) -> "ContentHashCode":
        _l = L(cls.__name__).gm("create")
        _code = Code.create(code)
        if not isinstance(_code, ContentHashCode):
            raise ValueError(_l.c("InvalidCode"))
        return _code


@dataclass
class ModuleCode(ContentCode):
    _l = L()
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
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")
        self.module_type = self.split[5]
        self.module_id = self.split[6]
        self.url = URLManager.getModule(self.year, self.module_type, self.module_id)

    @classmethod
    def create(cls, code: str) -> "ModuleCode":
        _l = L(cls.__name__).gm("create")
        _code = Code.create(code)
        if not isinstance(_code, ModuleCode):
            raise ValueError(_l.c("InvalidCode"))
        return _code

    def createModuleCode(self, tag):
        raise NotImplementedError(self._l.c("NotImplemented"))


@dataclass
class ModuleHashCode(ModuleCode, HashCode):
    _l = L()
    _attrs = ModuleCode._attrs | HashCode._attrs
    _types = ModuleCode._types | HashCode._types

    def __post_init__(self):
        ModuleCode.__post_init__(self)
        HashCode.__post_init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")

    @classmethod
    def create(cls, code: str) -> "ModuleHashCode":
        _l = L(cls.__name__).gm("create")
        _code = Code.create(code)
        if not isinstance(_code, ModuleHashCode):
            raise ValueError(_l.c("InvalidCode"))
        return _code
