from dataclasses import dataclass

from letusc.logger import Log

from .PageBase import PageBase
from .PageDatabase import PageDatabase


@dataclass
class Page(PageDatabase, PageBase):
    __logger = Log("Model.Page")

    def ___post_init___(self):
        object = self.pull()
        self.from_api(object)

    @classmethod
    def from_code(cls, code: str) -> "Page":
        try:
            code_split = code.split(":")
            if len(code_split) != 3:
                raise ValueError
        except Exception as e:
            raise ValueError("Model.Page.from_api:InvalidData") from e
        else:
            match code_split[1]:
                case "course":
                    return CoursePage(code)
                case _:
                    raise ValueError("Model.Page.from_api:UnknownType")


@dataclass
class CoursePage(Page):
    __logger = Log("Model.CoursePage")

    def __post_init__(self):
        super().___post_init___()


__all__ = [
    "Page",
    "CoursePage",
]
