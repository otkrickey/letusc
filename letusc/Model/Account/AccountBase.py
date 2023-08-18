from dataclasses import dataclass, field

from letusc.logger import Log
from letusc.Model.BaseModel import BaseModel
from letusc.Model.Discord.DiscordUser import DiscordUserBase
from letusc.Model.Letus.LetusUser import LetusUserBase


@dataclass
class AccountBase(BaseModel):
    __logger = Log("Model.AccountBase")
    # [must]
    multi_id: str  # 7 or 18 digit
    # [optional]
    student_id: str = field(init=False)  # 7 digit
    discord_id: str = field(init=False)  # 18 digit
    # [object]
    Discord: DiscordUserBase = field(init=False)
    Letus: LetusUserBase = field(init=False)

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
