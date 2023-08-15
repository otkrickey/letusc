from letusc.util import year


class LetusAccount:
    code: str
    year: int
    discord_id: str
    email: str | None
    encrypted_password: str | None
    cookie: dict = {}

    sync = False

    def __init__(self, code: str):
        self.code = code
        self.year = int(year)
        code_split = code.split(':')
        if len(code_split) == 1:
            self.discord_id = code_split[0]
            self.email = None
            self.encrypted_password = None
        elif len(code_split) == 3:
            self.discord_id = code_split[0]
            self.email = code_split[1]
            self.encrypted_password = code_split[2]
        else:
            raise ValueError(f'invalid code: {code}')

    def export(self):
        return {
            'discord_id': self.discord_id,
            'email': self.email,
            'encrypted_password': self.encrypted_password,
            'cookie': self.cookie,
        }
