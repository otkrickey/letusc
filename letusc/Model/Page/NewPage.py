from dataclasses import dataclass, field
from datetime import datetime

import bs4
from bs4 import BeautifulSoup

import letusc.PageParser as parser
from letusc.logger import Log
from letusc.URLManager import URLManager

from .Page import Page


@dataclass
class NewPage(Page):
    __logger = Log("Model.Page.NewPage")

    def __post_init__(self):
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

    def bind(self, object: dict):
        __logger = Log("Model.Page.bind")
        if "code" in object and isinstance(object["code"], str):
            self.code = object["code"]
        elif (
            "accounts" in object
            and isinstance(object["accounts"], list)
            and all(isinstance(account, str) for account in object["accounts"])
        ):
            self.accounts = object["accounts"]
        elif "title" in object and isinstance(object["title"], str):
            self.title = object["title"]
        elif "hash" in object and isinstance(object["hash"], str):
            self.hash = object["hash"]
        elif "timestamp" in object and isinstance(object["timestamp"], datetime):
            self.timestamp = object["timestamp"]
        else:
            __logger.error(f"InvalidData: {object}")
            raise ValueError("Model.Page.bind:InvalidData")

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
    __logger = Log("Model.CoursePage")


__all__ = [
    "NewPage",
    "NewCoursePage",
]
