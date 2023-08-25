from dataclasses import dataclass, field
from datetime import datetime

import bs4

import letusc.PageParser as parser
from letusc.logger import Log
from letusc.URLManager import URLManager

from .Module import Module


@dataclass
class NewModule(Module):
    __logger = Log("Model.Module.NewModule")

    def __post_init__(self):
        try:
            code_split = self.code.split(":")
            if len(code_split) != 7:
                raise ValueError
        except Exception as e:
            raise ValueError("Model.Content.from_api:InvalidData") from e
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
        try:
            code_split = code.split(":")
            if len(code_split) != 7:
                raise ValueError
        except Exception as e:
            raise ValueError("Model.Module.from_api:InvalidData") from e
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
                case _:
                    return NewModule(code)

    def parse(self, el: bs4.Tag):
        title_el = el.find(class_="activity-item", attrs={"data-activityname": True})
        title = (
            title_el.attrs["data-activityname"]
            if isinstance(title_el, bs4.Tag)
            else "<Error:NoTitleFound>"
        )

        url_el = el.find("a", {"class": "aalink"})
        module_url = (
            url_el.attrs["href"]
            if isinstance(url_el, bs4.Tag)
            else "<Error:NoURLFound>"
        )

        main_el = el.find("div", {"class": "description"})
        main = parser.tag_filter(main_el)
        main = parser.text_filter(main, hash=False, pretty=1, no_script=False)

        updated_at_el = el.find("span", {"class": "resourcelinkdetails"})
        uploaded_at = parser.tag_filter(updated_at_el)

        hash = parser.hash(parser.text_filter(str(el)))

        self.title = title
        self.module_url = module_url
        self.main = main
        self.uploaded_at = uploaded_at
        self.hash = hash
        self.timestamp = datetime.now()

        self.check()

    def bind_info(self, object: dict):
        try:
            title = object["title"]
            module_url = object["module_url"]
            main = object["main"]
            hash = object["hash"]
            timestamp = object["timestamp"]
            if not isinstance(title, str):
                title = None
            if not isinstance(module_url, str):
                module_url = None
            if not isinstance(main, str):
                main = None
            if not isinstance(hash, str):
                raise ValueError
            if not isinstance(timestamp, datetime):
                if not isinstance(timestamp, str):
                    raise ValueError
                timestamp = datetime.fromisoformat(timestamp)
        except Exception as e:
            raise ValueError("Model.Module.LabelModule:InvalidData") from e
        else:
            self.title = title
            self.module_url = module_url
            self.main = main
            self.hash = hash
            self.timestamp = timestamp


@dataclass
class NewLabelModule(NewModule):
    __logger = Log("Model.Module.NewLabelModule")

    main: str = field(init=False)


@dataclass
class NewPageModule(NewModule):
    __logger = Log("Model.Module.NewPageModule")

    title: str = field(init=False)
    module_url: str = field(init=False)


@dataclass
class NewURLModule(NewModule):
    __logger = Log("Model.Module.NewURLModule")

    title: str = field(init=False)
    module_url: str = field(init=False)


@dataclass
class NewResourceModule(NewModule):
    __logger = Log("Model.Module.NewResourceModule")

    title: str = field(init=False)
    module_url: str = field(init=False)
    uploaded_at: str = field(init=False)


__all__ = [
    "NewModule",
    "NewLabelModule",
    "NewPageModule",
    "NewURLModule",
    "NewResourceModule",
]
