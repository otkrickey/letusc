from dataclasses import dataclass, field

from ..logger import L
from .base import BaseModel, attrs, from_api_attrs, to_api_attrs, types

__all__ = [
    "Cookie",
]


@dataclass
class Cookie(BaseModel):
    _l = L()
    _attrs = BaseModel._attrs | attrs(["name", "value", "year", "domain"])
    _types = BaseModel._types | types(
        [
            ("name", "Name", str),
            ("value", "Value", str),
            ("year", "Year", str),
            ("domain", "Domain", str),
        ]
    )
    _from_api_attrs = BaseModel._from_api_attrs | from_api_attrs(
        [
            ("name", str, lambda obj: obj["name"]),
            ("value", str, lambda obj: obj["value"]),
            ("year", str, lambda obj: obj["year"]),
        ]
    )
    _to_api_attrs = BaseModel._to_api_attrs | to_api_attrs(
        [
            ("name", lambda self: self.name),
            ("value", lambda self: self.value),
            ("year", lambda self: self.year),
        ]
    )

    name: str
    value: str
    year: str
    domain: str = field(init=False)

    def __post_init__(self):
        BaseModel.__post_init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")
        self.domain = "letus.ed.tus.ac.jp"  # TODO: `{host}/{year}`
        self.key_name = "value"
        self.key = self.value

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

    def to_dict(self) -> dict:
        return {self.name: self.value}
