from dataclasses import dataclass, field

from letusc.logger import Log

from .base import BaseModel


@dataclass
class Cookie(BaseModel):
    _logger = Log("Model.Cookie")
    name: str
    value: str
    year: str
    domain: str = field(init=False)

    def __post_init__(self):
        self.domain = "letus.ed.tus.ac.jp"  # TODO: `{host}/{year}`

    @classmethod
    def from_api(cls, cookie: dict) -> "Cookie":
        try:
            name = cookie["name"]
            value = cookie["value"]
            year = cookie["year"]
        except KeyError as e:
            raise KeyError("Model.Cookie.from_api:KeyError") from e
        else:
            return cls(name=name, value=value, year=year)

    def to_api(self) -> dict:
        return {
            "name": self.name,
            "value": self.value,
            "year": self.year,
        }
