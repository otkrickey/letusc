from dataclasses import dataclass, field
from datetime import datetime

from letusc.logger import Log
from letusc.Model.BaseModel import BaseModel
from letusc.URLManager import URLManager


@dataclass
class ContentBase(BaseModel):
    __logger = Log("Model.ContentBase")
    code: str  # `year:page_type:page_id:content_type:content_id`

    year: str = field(init=False)
    page_type: str = field(init=False)
    page_id: str = field(init=False)
    content_type: str = field(init=False)
    content_id: str = field(init=False)
    url: str = field(init=False)

    title: str = field(init=False)
    main: str = field(init=False)
    modules: list[str] = field(init=False)  # `module_type:module_id:module_hash`[]

    hash: str = field(init=False)
    timestamp: datetime = field(init=False)

    def from_api(self, object: dict) -> None:
        try:
            code = object["code"]
            if not isinstance(code, str):
                raise ValueError
            code_split = code.split(":")
            if len(code_split) != 5:
                raise ValueError
            title = object["title"]
            main = object["main"]
            modules = object["modules"]
            hash = object["hash"]
            timestamp = object["timestamp"]
            if not isinstance(title, str):
                raise ValueError
            if not isinstance(main, str):
                raise ValueError
            if not isinstance(modules, list):
                raise ValueError
            if not all(isinstance(module, str) for module in modules):
                raise ValueError
            if not isinstance(hash, str):
                raise ValueError
            if not isinstance(timestamp, datetime):
                timestamp = datetime.now()
        except Exception as e:
            raise ValueError("Model.Content.from_api:InvalidData") from e
        else:
            self.year = code_split[0]
            self.page_type = code_split[1]
            self.page_id = code_split[2]
            self.content_type = code_split[3]
            self.content_id = code_split[4]
            self.url = URLManager.getPage(self.year, self.page_type, self.page_id)
            self.title = title
            self.main = main
            self.modules = modules
            self.hash = hash
            self.timestamp = timestamp
        return

    def to_api(self) -> dict:
        return {
            "code": self.code,
            "title": self.title,
            "main": self.main,
            "modules": self.modules,
            "hash": self.hash,
            "timestamp": self.timestamp,
        }
