from dataclasses import dataclass, field

from ..logger import get_logger
from ..util import env
from .base import BaseModel, attrs, to_api_attrs, types
from .cookie import Cookie

logger = get_logger(__name__)

__all__ = [
    "LetusUserBase",
    "LetusUser",
    "LetusUserWithPassword",
    "LetusUserWithCookies",
]


@dataclass
class LetusUserBase(BaseModel):
    _attrs = BaseModel._attrs | attrs(["student_id", "email", "password", "cookies"])
    _types = BaseModel._types | types(
        [
            ("student_id", "StudentID", str),
            ("email", "Email", str),
            ("password", "Password", str),
            ("cookies", "Cookies", list[Cookie]),
        ]
    )
    _to_api_attrs = BaseModel._to_api_attrs | to_api_attrs(
        [
            ("email", lambda self: self.email),
            ("password", lambda self: self.password),
            ("cookies", lambda self: [cookie.to_api() for cookie in self.cookies]),
        ]
    )

    student_id: str
    password: str | None = None
    cookies: list["Cookie"] | None = None

    email: str = field(init=False)

    def __post_init__(self):
        BaseModel.__post_init__(self)
        self.email = f"{self.student_id}@{env('TUS_EMAIL_HOST')}"
        self.cookies = self.cookies or []
        self.key_name = "email"
        self.key = self.email

    @classmethod
    def from_api(cls, object: dict) -> "LetusUserBase":
        try:
            student_id = object["student_id"]
        except KeyError as e:
            raise KeyError("Model.LetusUserBase.from_api:KeyError") from e
        else:
            try:
                password = object["Letus"]["password"]
                cookies = object["Letus"]["cookies"]
            except KeyError as e:
                return LetusUser(student_id=student_id)
            else:
                if password and cookies:
                    return LetusUserWithCookies(
                        student_id=student_id,
                        password=password,
                        cookies=[Cookie.from_api(cookie) for cookie in cookies],
                    )
                elif password:
                    return LetusUserWithPassword(
                        student_id=student_id,
                        password=password,
                    )
                else:
                    return LetusUser(student_id=student_id)


@dataclass
class LetusUser(LetusUserBase):
    _types = LetusUserBase._types | types(
        [
            ("student_id", "StudentID", str),
            ("email", "Email", str),
        ]
    )

    def __post_init__(self):
        LetusUserBase.__post_init__(self)


@dataclass
class LetusUserWithPassword(LetusUser):
    _types = LetusUser._types | types([("password", "Password", str)])

    password: str

    def __post_init__(self):
        LetusUser.__post_init__(self)


@dataclass
class LetusUserWithCookies(LetusUserWithPassword):
    _types = LetusUserWithPassword._types | types(
        [("cookies", "Cookies", list[Cookie])]
    )

    cookies: list["Cookie"]

    def __post_init__(self):
        LetusUserWithPassword.__post_init__(self)
