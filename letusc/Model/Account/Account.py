from dataclasses import dataclass

from letusc.logger import Log
from letusc.Model.Discord import DiscordUser
from letusc.Model.Letus import LetusUser

from .AccountBase import AccountBase
from .AccountDatabase import AccountDatabase


@dataclass
class Account(AccountDatabase, AccountBase):
    __logger = Log("Model.Account")

    def __post_init__(self):
        object = self.pull()
        try:
            student_id = object["student_id"]
            if not isinstance(student_id, str):
                raise ValueError
        except Exception as e:
            raise ValueError("Model.Account.__post_init__:InvalidStudentID") from e
        else:
            self.student_id = student_id

        try:
            discord_id = object["discord_id"]
            if not isinstance(discord_id, str):
                raise ValueError
        except Exception as e:
            raise ValueError("Model.Account.__post_init__:InvalidDiscordID") from e
        else:
            self.discord_id = discord_id

        try:
            letus = object["Letus"]
            if not isinstance(letus, dict):
                raise ValueError
            Letus = LetusUser.from_api(letus)
            if not isinstance(Letus, LetusUser):
                raise ValueError
        except Exception as e:
            raise ValueError("Model.Account.__post_init__:InvalidLetus") from e
        else:
            self.Letus = Letus

        try:
            Discord = object["Discord"]
            if not isinstance(Discord, dict):
                raise ValueError
        except Exception as e:
            raise ValueError("Model.Account.__post_init__:InvalidDiscord") from e
        else:
            self.Discord = DiscordUser.from_api(Discord)


__all__ = [
    "Account",
]
