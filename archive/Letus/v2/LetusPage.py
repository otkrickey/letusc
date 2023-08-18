from src.database.v1.AccountManager import AccountManager
from src.Letus.v2.LetusAccount import LetusAccount
from src.util import year_current


class LetusPage:
    key: str  # `year:type:letus`
    code: str  # `year:type:letus`(fetching) or `year:type:letus:guild:channel:user`(initializing)
    year: int
    type: str
    letus_id: int
    accounts: list[str] | None  # `guild:channel:user`[]
    url: str

    LA: LetusAccount
    cookie: dict[str, str] = {}

    sync = False

    def __init__(self, code: str):
        self.code = code
        code_split = code.split(":")
        if len(code_split) == 3:
            self.key = code
            self.year = int(code_split[0])
            self.type = code_split[1]
            self.letus_id = int(code_split[2])
        elif len(code_split) == 6:
            self.key = ":".join(code_split[:3])
            self.accounts = [":".join(code_split[3:])]
        else:
            raise ValueError(f"invalid code: `{code}`")

        self.year = int(code_split[0])
        self.type = code_split[1]
        self.letus_id = int(code_split[2])
        self.url = self.__get_url()

        self.struct()

    def __get_url(self):
        origin = "https://letus.ed.tus.ac.jp" + (
            f"/{self.year}" if self.year != year_current else ""
        )
        if self.type == "course":
            return f"{origin}/course/view.php?id={self.letus_id}"
        else:
            raise ValueError(f"unknown type: {self.type}")

    def struct(self):
        if len(self.code.split(":")) == 6:
            self.LA = LetusAccount(self.code.split(":")[5])
            AccountManager(self.LA).check()
            self.cookie = self.LA.cookie

    def export(self):
        return {
            "key": self.key,  # `{year}:{type}:{letus}`
            "code": self.code,  # `{year}:{type}:{letus}:{guild}:{category}:{channel}:{user}`(initializing)
            "url": self.url,  # `{LetusPageV2.__origin_url}/{year}course/view.php?id={self.letus_id}`
            "year": self.year,  # `{year}`
            "type": self.type,  # `{type}`
            "letus_id": self.letus_id,
            "accounts": self.accounts,
        }
