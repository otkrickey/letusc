from dataclasses import dataclass, field

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

    def from_api(self, object: dict) -> None:
        try:
            student_id = object["student_id"]
            discord_id = object["discord_id"]
            Letus = LetusUser.from_api(object)
            Discord = DiscordUser.from_api(object)
            if not isinstance(student_id, str):
                raise ValueError
            if not isinstance(discord_id, str):
                raise ValueError
            if not isinstance(Letus, LetusUser):
                raise ValueError
            if not isinstance(Discord, DiscordUser):
                raise ValueError
        except Exception as e:
            raise ValueError("Model.Account.from_api:InvalidData") from e
        else:
            self.student_id = student_id
            self.discord_id = discord_id
            self.Letus = Letus
            self.Discord = Discord

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
