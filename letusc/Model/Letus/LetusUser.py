from dataclasses import dataclass, field
from typing import Optional, Union

from letusc.logger import Log
from letusc.Model.BaseModel import BaseModel
from letusc.util import env

from .Cookie import Cookie


@dataclass
class LetusUserBase(BaseModel):
    __logger = Log("Model.LetusUserBase")
    student_id: str
    encrypted_password: Optional[str] = None
    email: str = field(init=False)
    cookies: Optional[list["Cookie"]] = None

    def __post_init__(self):
        self.email = f"{self.student_id}@{env('TUS_EMAIL_HOST')}"

    @classmethod
    def from_api(
        cls, object: dict
    ) -> Union["LetusUser", "LetusUserWithPassword", "LetusUserWithCookies"]:
        try:
            student_id = object["student_id"]
        except KeyError as e:
            cls.__logger.error(f"object must have student_id: {e}")
            raise KeyError("Model.LetusUserBase.from_api:KeyError")
        else:
            try:
                encrypted_password = object["Letus"]["encrypted_password"]
                cookies = object["Letus"]["cookies"]
            except KeyError as e:
                cls.__logger.warn(f"object has no key: {e}")
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
            "Letus": {
                "encrypted_password": self.encrypted_password,
                "cookies": cookies,
            },
        }


@dataclass
class LetusUser(LetusUserBase):
    __logger = Log("Model.LetusUser")


@dataclass
class LetusUserWithPassword(LetusUser):
    __logger = Log("Model.LetusUserWithPassword")
    encrypted_password: str


@dataclass
class LetusUserWithCookies(LetusUserWithPassword):
    __logger = Log("Model.LetusUserWithCookies")
    cookies: list["Cookie"]