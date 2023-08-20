from dataclasses import dataclass

from letusc.logger import Log
from letusc.Model.Account import Account
from letusc.URLManager import URLManager

from .PageBase import PageBase
from .PageDatabase import PageDatabase


@dataclass
class Page(PageDatabase, PageBase):
    __logger = Log("Model.Page")

    def __post_init__(self):
        object = self.pull()
        self.from_api(object)

    def from_api(self, object: dict) -> None:
        try:
            code = object["code"]
            code_split = code.split(":")
            if len(code_split) != 3:
                raise ValueError
            self.year = code_split[0]
            self.type = code_split[1]
            self.object_id = code_split[2]
        except Exception as e:
            raise ValueError("Model.Page.from_api:InvalidCode") from e

        try:
            accounts = object["accounts"]
            if not isinstance(accounts, list):
                raise ValueError
            if not all(isinstance(account, str) for account in accounts):
                raise ValueError
            self.accounts = accounts
        except Exception as e:
            raise ValueError("Model.Page.from_api:InvalidAccounts") from e

        self.url = URLManager.getPage(self.code)


__all__ = [
    "Page",
]
