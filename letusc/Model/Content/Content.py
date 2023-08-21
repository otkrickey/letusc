from dataclasses import dataclass

from letusc.logger import Log

from .ContentBase import ContentBase
from .ContentDatabase import ContentDatabase


@dataclass
class Content(ContentDatabase, ContentBase):
    __logger = Log("Model.Content")

    def ___post_init___(self):
        object = self.pull()
        self.from_api(object)

    @classmethod
    def from_code(cls, code: str) -> "SectionContent":
        try:
            code_split = code.split(":")
            if len(code_split) != 5:
                raise ValueError
        except Exception as e:
            raise ValueError("Model.Content.from_api:InvalidData") from e
        else:
            match code_split[3]:
                case "section":
                    return SectionContent(code)
                case _:
                    raise ValueError("Model.Content.from_api:UnknownType")


@dataclass
class SectionContent(Content):
    __logger = Log("Model.Content.SectionContent")

    def __post_init__(self):
        super().___post_init___()


__all__ = [
    "Content",
    "SectionContent",
]
