from dataclasses import dataclass, field
from typing import Optional, Union
from letusc.logger import Log
from letusc.util import env


@dataclass
class LetusUser:
    __logger = Log("Model.LetusUser")
    # [must]
    student_id: str
    # [optional]
    encrypted_password: Optional[str] = None
    # [auto]
    email: str = field(init=False)
    # [api]
    cookies: Optional[list["Cookie"]] = None

    def __post_init__(self):
        self.email = f"{self.student_id}@{env('TUS_EMAIL_HOST')}"

    @classmethod
    def from_api(
        cls, account: dict
    ) -> Union["LetusUser", "LetusUserWithPassword", "LetusUserWithCookies"]:
        try:
            student_id = account["student_id"]
            encrypted_password = account["Letus"]["encrypted_password"]
            cookies = account["Letus"]["cookies"]
        except KeyError as e:
            cls.__logger.warn(f"account has no key: {e}")
            try:
                student_id = account["student_id"]
            except KeyError as e:
                cls.__logger.error(f"account must have student_id: {e}")
                raise Exception("Model.LetusUser.from_api:KeyError")
            else:
                return cls(student_id=student_id)
        else:
            if encrypted_password:
                if cookies:
                    return LetusUserWithCookies(
                        student_id=student_id,
                        encrypted_password=encrypted_password,
                        cookies=[Cookie.from_api(cookie) for cookie in cookies],
                    )
                else:
                    return LetusUserWithPassword(
                        student_id=student_id,
                        encrypted_password=encrypted_password,
                    )
            else:
                return cls(student_id=student_id)

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
class LetusUserWithPassword(LetusUser):
    __logger = Log("Model.LetusUserWithPassword")
    encrypted_password: str


@dataclass
class LetusUserWithCookies(LetusUserWithPassword):
    __logger = Log("Model.LetusUserWithCookies")
    cookies: list["Cookie"]


@dataclass
class Cookie:
    name: str
    value: str
    year: str
    # [auto]
    domain: str = field(init=False)

    def __post_init__(self):
        self.domain = "letus.ed.tus.ac.jp"  # TODO: `{host}/{year}`

    @classmethod
    def from_api(cls, cookie: dict) -> "Cookie":
        return cls(
            name=cookie["name"],
            value=cookie["value"],
            year=cookie["year"],
        )


    def to_api(self) -> dict:
        return {
            "name": self.name,
            "value": self.value,
            "year": self.year,
        }
