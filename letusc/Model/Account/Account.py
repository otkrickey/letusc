from dataclasses import dataclass

from letusc.logger import Log

from .AccountBase import AccountBase
from .AccountDatabase import AccountDatabase


@dataclass
class Account(AccountDatabase, AccountBase):
    __logger = Log("Model.Account")

    def __post_init__(self):
        object = self.pull()
        self.from_api(object)


__all__ = [
    "Account",
]
