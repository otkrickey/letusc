from dataclasses import dataclass, field
from datetime import datetime

import bs4
from aiohttp import ClientResponseError
from bs4 import BeautifulSoup

from ..db import DBManager
from ..logger import L
from ..session import SessionManager
from .base import (
    BaseDatabase,
    BaseModel,
    BaseParser,
    attrs,
    from_api_attrs,
    to_api_attrs,
    types,
)
from .code import ContentHashCode, PageCode
from .content import NewContent
from .cookie import Cookie

__all__ = [
    "PageBase",
    "Page",
    "CoursePage",
    "PageParser",
    "NewPage",
    "NewCoursePage",
]


@dataclass
class PageBase(PageCode, BaseDatabase, BaseModel):
    _l = L()
    _attrs = (
        BaseModel._attrs
        | PageCode._attrs
        | attrs(
            [
                "accounts",
                "chat",
                "title",
                "contents",
                "hash",
                "timestamp",
            ]
        )
    )
    _types = (
        BaseModel._types
        | PageCode._types
        | types(
            [
                ("accounts", "Accounts", list[str]),
                ("chat", "Chat", dict[str, str]),
                ("title", "Title", str),
                ("contents", "Contents", dict[str, ContentHashCode]),
                ("hash", "Hash", str),
                ("timestamp", "Timestamp", datetime),
            ]
        )
    )
    _from_api_attrs = (
        BaseModel._from_api_attrs
        | PageCode._from_api_attrs
        | from_api_attrs(
            [
                ("accounts", list, lambda obj: obj["accounts"]),
                (
                    "chat",
                    dict[str, str],
                    lambda obj: {k: v for k, v in obj["chat"].items()},
                ),
                ("title", str, lambda obj: obj["title"]),
                (
                    "contents",
                    dict[str, ContentHashCode],
                    lambda obj: {
                        c.code: c
                        for c in [
                            ContentHashCode.create(f"{k}:{v}")
                            for k, v in obj["contents"].items()
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
        | PageCode._to_api_attrs
        | to_api_attrs(
            [
                ("accounts", lambda self: self.accounts),
                ("chat", lambda self: {k: v for k, v in self.chat.items()}),
                ("title", lambda self: self.title),
                (
                    "contents",
                    lambda self: {k: v.hash for k, v in self.contents.items()},
                ),
                ("hash", lambda self: self.hash),
                ("timestamp", lambda self: self.timestamp),
            ]
        )
    )

    collection = DBManager.get_collection("letus", "pages")
    code: str

    accounts: list[str] = field(init=False, default_factory=list)
    chat: dict[str, str] = field(init=False, default_factory=dict)

    title: str = field(init=False)
    contents: dict[str, ContentHashCode] = field(init=False, default_factory=dict)
    hash: str = field(init=False)
    timestamp: datetime = field(init=False)

    def __post_init__(self):
        BaseModel.__post_init__(self)
        PageCode.__post_init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")

    async def get(self, cookie: Cookie) -> bs4.BeautifulSoup:
        _l = self._l.gm("get")
        _l.info(f"Requesting page: {self.url}")
        session = SessionManager.get()
        session.cookie_jar.update_cookies(cookie.to_dict())
        async with session.get(self.url) as response:
            try:
                response.raise_for_status()
            except ClientResponseError as e:
                match e.status:
                    case 404:
                        _l.error(f"Page not found: {self.url}")
                        raise Exception(_l.c("NotFound")) from e
                    case 503:
                        _l.error(f"Service unavailable: {self.url}")
                        raise Exception(_l.c("ServiceUnavailable")) from e
                    case _:
                        _l.warn(f"Error {e.status} for URL: {self.url}")
                        raise Exception(_l.c("UnknownHTTPError")) from e
            else:
                _l.debug(f"Successfully fetched URL: {self.url}")
                html = await response.text()
                return BeautifulSoup(html, "html.parser")


@dataclass
class Page(PageBase):
    _l = L()

    def __post_init__(self):
        PageBase.__post_init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")

    @classmethod
    async def pull(cls, code: str) -> "Page":
        _l = L(cls.__name__).gm("pull")
        _code = PageCode.create(code)
        match _code.page_type:
            case "course":
                page = CoursePage(code=code)
            case _:
                raise ValueError(_l.c("UnknownPageType"))
        page.from_api(await page._pull())
        return page


@dataclass
class CoursePage(Page):
    _l = L()

    def __post_init__(self):
        Page.__post_init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")


@dataclass
class PageParser(BaseParser, PageBase):
    _l = L()

    contents: dict[str, NewContent] = field(init=False, default_factory=dict)

    def __post_init__(self):
        PageBase.__post_init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")

    async def _parse(self, soup: BeautifulSoup) -> None:
        _l = self._l.gm("_parse")
        self.title = self._get_title(soup.find(attrs={"class": "page-header-headings"}))
        self.contents = {
            c.code: c
            for c in [
                await NewContent.parse(self, content_el)
                for content_el in soup.find_all(attrs={"data-for": "section"})
            ]
        }
        self.hash = self._get_hash(soup.find("section", {"id": "region-main"}))
        self.timestamp = datetime.now()
        self.check()


@dataclass
class NewPage(PageParser, PageBase):
    _l = L()

    def __post_init__(self):
        PageBase.__post_init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")

    @classmethod
    async def parse(cls, code: PageCode, cookie: Cookie) -> "NewPage":
        _l = L(cls.__name__).gm("parse")
        match code.page_type:
            case "course":
                page = NewCoursePage(code.code)
            case _:
                raise ValueError(_l.c("UnknownPageType"))
        soup = await page.get(cookie)
        await page._parse(soup)
        return page

    def bind_chat(self, chat: dict[str, str]) -> None:
        self.chat.update(chat)

    def bind_account(self, account: str) -> None:
        self.accounts.append(account)


@dataclass
class NewCoursePage(NewPage):
    _l = L()

    def __post_init__(self):
        NewPage.__post_init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")
