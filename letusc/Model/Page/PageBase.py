from dataclasses import dataclass, field
from datetime import datetime

from letusc.logger import Log
from letusc.Model.BaseModel import BaseModel
from letusc.URLManager import URLManager


@dataclass
class PageBase(BaseModel):
    __logger = Log("Model.PageBase")
    code: str  # `year:page_type:page_id`

    year: str = field(init=False)
    page_type: str = field(init=False)
    page_id: str = field(init=False)
    url: str = field(init=False)

    # `multi_id`[]
    accounts: list[str] = field(default_factory=list, init=False)

    title: str = field(init=False)
    # `content_type:content_id:content_hash`[]
    contents: list[str] = field(default_factory=list, init=False)

    hash: str = field(init=False)
    timestamp: datetime = field(init=False)

    def from_api(self, object: dict) -> None:
        try:
            code = object["code"]
            code_split = code.split(":")
            if len(code_split) != 3:
                raise ValueError

            accounts = object["accounts"]
            if not isinstance(accounts, list):
                raise ValueError
            if not all(isinstance(account, str) for account in accounts):
                raise ValueError
            self.accounts = accounts

            title = object["title"]
            hash = object["hash"]
            timestamp = object["timestamp"]
            contents = object["contents"]
            if not isinstance(title, str):
                raise ValueError
            if not isinstance(hash, str):
                raise ValueError
            if not isinstance(timestamp, datetime):
                timestamp = datetime.now()
            if not isinstance(contents, list):
                raise ValueError
            if not all(isinstance(content, str) for content in contents):
                raise ValueError
        except Exception as e:
            raise ValueError("Model.Page.from_api:InvalidData") from e
        else:
            self.year = code_split[0]
            self.page_type = code_split[1]
            self.page_id = code_split[2]
            self.url = URLManager.getPage(self.year, self.page_type, self.page_id)
            self.title = title
            self.contents = contents
            self.hash = hash
            self.timestamp = timestamp
        return

    def to_api(self) -> dict:
        return {
            "code": self.code,
            "accounts": self.accounts,
            "title": self.title,
            "contents": self.contents,
            "hash": self.hash,
            "timestamp": self.timestamp,
        }


__all__ = [
    "PageBase",
]
