from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from letusc.logger import Log
from letusc.Model.BaseModel import BaseModel
from letusc.URLManager import URLManager


@dataclass
class ModuleBase(BaseModel):
    __logger = Log("Model.ModuleBase")
    code: str  # `year:page_type:page_id:content_type:content_id:module_type:module_id`

    year: str = field(init=False)
    page_type: str = field(init=False)
    page_id: str = field(init=False)
    content_type: str = field(init=False)
    content_id: str = field(init=False)
    module_type: str = field(init=False)
    module_id: str = field(init=False)
    url: str = field(init=False)

    title: Optional[str] = field(init=False)
    module_url: Optional[str] = field(init=False)
    main: Optional[str] = field(init=False)
    uploaded_at: Optional[str] = field(init=False)

    hash: str = field(init=False)
    timestamp: datetime = field(init=False)

    def from_api(self, object: dict) -> None:
        try:
            code = object["code"]
            if not isinstance(code, str):
                raise ValueError
            code_split = code.split(":")
            if len(code_split) != 7:
                raise ValueError
            title = object["title"]
            module_url = object["module_url"]
            main = object["main"]
            uploaded_at = object["uploaded_at"]
            hash = object["hash"]
            timestamp = object["timestamp"]
            if not isinstance(title, str):
                title = None
            if not isinstance(module_url, str):
                module_url = None
            if not isinstance(main, str):
                main = None
            if not isinstance(uploaded_at, str):
                uploaded_at = None
            if not isinstance(timestamp, datetime):
                timestamp = datetime.now()
        except Exception as e:
            raise ValueError("Model.Module.from_api:InvalidData") from e
        else:
            self.year = code_split[0]
            self.page_type = code_split[1]
            self.page_id = code_split[2]
            self.content_type = code_split[3]
            self.content_id = code_split[4]
            self.module_type = code_split[5]
            self.module_id = code_split[6]
            self.url = URLManager.getPage(self.year, self.page_type, self.page_id)
            self.title = title
            self.module_url = module_url
            self.main = main
            self.uploaded_at = uploaded_at
            self.hash = hash
            self.timestamp = timestamp
        return

    def to_api(self) -> dict:
        return {
            "code": self.code,
            "title": self.title,
            "module_url": self.module_url,
            "main": self.main,
            "uploaded_at": self.uploaded_at,
            "hash": self.hash,
            "timestamp": self.timestamp,
        }
