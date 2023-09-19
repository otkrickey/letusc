from dataclasses import dataclass, field

from letusc.logger import L
from letusc.util import env

from .base import BaseModel, attrs, to_api_attrs, types
from .cookie import Cookie

__all__ = [
    "LetusUserBase",
    "LetusUser",
    "LetusUserWithPassword",
    "LetusUserWithCookies",
]


@dataclass
class LetusUserBase(BaseModel):
    _l = L()
    _attrs = BaseModel._attrs | attrs(
        ["student_id", "email", "encrypted_password", "cookies"]
    )
    _types = BaseModel._types | types(
        [
            ("student_id", "StudentID", str),
            ("email", "Email", str),
            ("encrypted_password", "EncryptedPassword", str),
            ("cookies", "Cookies", list[Cookie]),
        ]
    )
    _to_api_attrs = BaseModel._to_api_attrs | to_api_attrs(
        [
            ("email", lambda self: self.email),
            ("encrypted_password", lambda self: self.encrypted_password),
            ("cookies", lambda self: [cookie.to_api() for cookie in self.cookies]),
        ]
    )

    student_id: str
    encrypted_password: str | None = None
    cookies: list["Cookie"] | None = None

    email: str = field(init=False)

    def __post_init__(self):
        BaseModel.__post_init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")
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
                encrypted_password = object["Letus"]["encrypted_password"]
                cookies = object["Letus"]["cookies"]
            except KeyError as e:
                return LetusUser(student_id=student_id)
            else:
                if encrypted_password and cookies:
                    return LetusUserWithCookies(
                        student_id=student_id,
                        encrypted_password=encrypted_password,
                        cookies=[Cookie.from_api(cookie) for cookie in cookies],
                    )
                elif encrypted_password:
                    return LetusUserWithPassword(
                        student_id=student_id,
                        encrypted_password=encrypted_password,
                    )
                else:
                    return LetusUser(student_id=student_id)


@dataclass
class LetusUser(LetusUserBase):
    _l = L()
    _types = LetusUserBase._types | types(
        [
            ("student_id", "StudentID", str),
            ("email", "Email", str),
        ]
    )

    def __post_init__(self):
        LetusUserBase.__post_init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")


@dataclass
class LetusUserWithPassword(LetusUser):
    _l = L()
    _types = LetusUser._types | types(
        [("encrypted_password", "EncryptedPassword", str)]
    )

    encrypted_password: str

    def __post_init__(self):
        LetusUser.__post_init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")


@dataclass
class LetusUserWithCookies(LetusUserWithPassword):
    _l = L()
    _types = LetusUserWithPassword._types | types(
        [("cookies", "Cookies", list[Cookie])]
    )

    cookies: list["Cookie"]

    def __post_init__(self):
        LetusUserWithPassword.__post_init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")
