from os import path
from typing import Literal
from urllib.parse import urlencode

from src.database.v1.AccountManager import AccountManager
from src.Letus.v2.LetusAccount import LetusAccount
from src.util import year_current


class LetusPage:
    __origin_url = "https://letus.ed.tus.ac.jp"
    __auth_url = "auth/shibboleth/index.php"
    __course_url = "course/view.php"

    type: Literal["all", "course"]
    year: int
    id: int | None

    def __init__(self, LA: LetusAccount):
        self.LetusAccount = LA
        self.year = year_current
        self.set_page_options()

    def set_page_options(self, type=None, year=None, id=None):
        self.type = type if type is not None else "all"
        self.year = year_current if year is None else year
        self.id = id

    def get_url(self, omit_year=False):
        base_url = (
            LetusPage.__origin_url
            if omit_year
            else path.join(LetusPage.__origin_url, str(self.year))
        )
        if self.type == "course":
            return f'{path.join(base_url, LetusPage.__course_url)}?{urlencode({"id": self.id})}'
        else:
            raise ValueError(f"unknown type: {self.type}")

    @staticmethod
    def origin_url(year=year_current, omit_year=False):
        return (
            LetusPage.__origin_url
            if year == year_current and omit_year
            else path.join(LetusPage.__origin_url, str(year))
        )

    @staticmethod
    def auth_url(year=year_current, omit_year=False):
        base_url = (
            LetusPage.__origin_url
            if year == year_current and omit_year
            else path.join(LetusPage.__origin_url, str(year))
        )
        return path.join(base_url, LetusPage.__auth_url)