from dataclasses import dataclass, field
from datetime import datetime

import bs4

import letusc.util.parser as parser
from letusc.logger import Log
from letusc.URLManager import URLManager

from .Module import Module


@dataclass
class NewModule(Module):
    __logger = Log("Model.Module.NewModule")

    def __post_init__(self):
        self.identify()
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
                case "folder":
                    return NewFolderModule(code)
                case "feedback":
                    return NewFeedbackModule(code)
                case _:
                    cls.__logger.error(f"Unknown module type: {code_split[5]}")
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
    __logger = Log("Model.Module.NewLabelModule")

    main: str = field(init=False)

    def parse(self, el: bs4.Tag):
        super().parse(el)
        self.module_url = None


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
    uploaded_at: datetime = field(init=False)


@dataclass
class NewFolderModule(NewModule):
    __logger = Log("Model.Module.NewFolderModule")

    title: str = field(init=False)


@dataclass
class NewFeedbackModule(NewModule):
    __logger = Log("Model.Module.NewFeedbackModule")

    title: str = field(init=False)
    module_url: str = field(init=False)


__all__ = [
    "NewModule",
    "NewLabelModule",
    "NewPageModule",
    "NewURLModule",
    "NewResourceModule",
    "NewFolderModule",
]
