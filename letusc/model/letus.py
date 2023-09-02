from dataclasses import dataclass, field

from letusc.logger import Log
from letusc.util import env

from .base import BaseModel
from .cookie import Cookie


@dataclass
class LetusUserBase(BaseModel):
    _logger = Log("Model.LetusUserBase")
    student_id: str
    encrypted_password: str | None = None
    email: str = field(init=False)
    cookies: list["Cookie"] | None = None

    def __post_init__(self):
        self.email = f"{self.student_id}@{env('TUS_EMAIL_HOST')}"

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

    def to_api(self) -> dict:
        cookies = []
        if self.cookies:
            cookies = [cookie.to_api() for cookie in self.cookies]
        return {
            "email": self.email,
            "encrypted_password": self.encrypted_password,
            "cookies": cookies,
        }


@dataclass
class LetusUser(LetusUserBase):
    _logger = Log("Model.LetusUser")


@dataclass
class LetusUserWithPassword(LetusUser):
    _logger = Log("Model.LetusUserWithPassword")
    encrypted_password: str


@dataclass
class LetusUserWithCookies(LetusUserWithPassword):
    _logger = Log("Model.LetusUserWithCookies")
    cookies: list["Cookie"]


__all__ = [
    "LetusUserBase",
    "LetusUser",
    "LetusUserWithPassword",
    "LetusUserWithCookies",
]
