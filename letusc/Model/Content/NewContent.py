from dataclasses import dataclass, field
from datetime import datetime

import bs4
import letusc.PageParser as parser
from letusc.logger import Log
from letusc.URLManager import URLManager

from .Content import Content


@dataclass
class NewContent(Content):
    __logger = Log("Model.Content.NewContent")

    # title: str
    # main: str

    # hash: str
    # timestamp: datetime

    def __post_init__(self):
        try:
            code_split = self.code.split(":")
            if len(code_split) != 5:
                raise ValueError
        except Exception as e:
            raise ValueError("Model.Content.from_api:InvalidData") from e
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
        try:
            code_split = code.split(":")
            if len(code_split) != 5:
                raise ValueError
        except Exception as e:
            raise ValueError("Model.Content.from_api:InvalidData") from e
        else:
            match code_split[3]:
                case "section":
                    return NewSectionContent(code)
                case _:
                    raise ValueError("Model.Content.from_api:UnknownType")

    def parse(self, el: bs4.Tag):
        title_el = el.find("h3", attrs={"data-for": "section_title"})
        if not isinstance(title_el, bs4.Tag):
            raise Exception("PageParser.get_content:TitleIsNotTag")
        title = title_el.text.lstrip().rstrip()

        main_el = el.find("div", {"class": "summarytext"})
        main = (parser.tag_filter(main_el) or "").lstrip().rstrip()

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
    "NewContent",
    "NewSectionContent",
]
