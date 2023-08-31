from dataclasses import dataclass, field
from typing import Callable

from letusc.logger import Log
from letusc.Model.BaseModel import BaseModel
from letusc.Model.Discord import DiscordUser
from letusc.Model.Discord.DiscordUser import DiscordUserBase
from letusc.Model.Letus import LetusUser
from letusc.Model.Letus.LetusUser import LetusUserBase


@dataclass
class AccountBase(BaseModel):
    __logger = Log("Model.AccountBase")
    multi_id: str  # 7 or 18 digit

    student_id: str = field(init=False)  # 7 digit
    discord_id: str = field(init=False)  # 18 digit
    Discord: DiscordUserBase = field(init=False)
    Letus: LetusUserBase = field(init=False)

    def identify(self) -> None:
        __logger = Log(f"{self.__logger}.identify")
        match len(self.multi_id):
            case 7:
                self.key_name = "student_id"
                self.key = self.multi_id
            case 18:
                self.key_name = "discord_id"
                self.key = self.multi_id
            case _:
                raise ValueError(f"{__logger}:InvalidMultiID")

    def from_api(
        self, object: dict, attrs: list[tuple[str, type, Callable]] = []
    ) -> None:
        attrs[:0] = [
            ("student_id", str, lambda obj: obj["student_id"]),
            ("discord_id", str, lambda obj: obj["discord_id"]),
            ("Letus", LetusUser, lambda obj: LetusUser.from_api(obj)),
            ("Discord", DiscordUser, lambda obj: DiscordUser.from_api(obj)),
        ]
        super().from_api(object, attrs=attrs)

    def to_api(self) -> dict:
        return {
            "student_id": self.student_id,
            "discord_id": self.discord_id,
            "Letus": self.Letus.to_api(),
            "Discord": self.Discord.to_api(),
        }


__all__ = [
    "AccountBase",
]
