from .logger import L
from .util import env

__all__ = [
    "URLManager",
]


class URLManager:
    _l = L()
    current_year = "2023"
    origin = env("URL_ORIGIN")
    icon = env("URL_ICON")
    thumbnail = env("URL_THUMBNAIL")
    github = env("URL_GITHUB")
    discord_webhook = env("URL_DISCORD_WEBHOOK_NOTIFY")
    discord_webhook_general = env("URL_DISCORD_WEBHOOK_GENERAL")

    def __init__(self):
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__init__")

    @staticmethod
    def getMongo():
        _l = L(URLManager.__name__).gm("getMongo")
        user = env("MONGO_USER")
        passwd = env("MONGO_PASS")
        host = env("MONGO_HOST")
        return f"mongodb+srv://{user}:{passwd}@{host}/?retryWrites=true&w=majority"

    @staticmethod
    def getOrigin(year=current_year, omit_year=True):
        _l = L(URLManager.__name__).gm("getOrigin")
        prefix = URLManager.origin
        if year != URLManager.current_year or not omit_year:
            prefix += f"/{year}"
        return prefix

    @staticmethod
    def getAuth(year=current_year, omit_year=True):
        _l = L(URLManager.__name__).gm("getAuth")
        prefix = URLManager.getOrigin(year, omit_year)
        return f"{prefix}/auth/shibboleth/index.php"

    @staticmethod
    def fromCode(code: str):
        _l = L(URLManager.__name__).gm("fromCode")
        try:
            code_split = code.split(":")
            if len(code_split) != 3:
                raise ValueError
            year = code_split[0]
            type = code_split[1]
            object_id = code_split[2]
        except Exception as e:
            raise ValueError(_l.c("InvalidCode")) from e
        else:
            return year, type, object_id

    @staticmethod
    def getPage(year: str, type: str, object_id: str):
        _l = L(URLManager.__name__).gm("getPage")
        prefix = URLManager.origin
        middle = f"/{year}" if year != "2023" else ""
        suffix = f"/{type}/view.php?id={object_id}"
        return f"{prefix}{middle}{suffix}"

    @staticmethod
    def getPageByCode(page_code: str):
        _l = L(URLManager.__name__).gm("getPageByCode")
        try:
            code_split = page_code.split(":")
            if len(code_split) != 3:
                raise ValueError
            year = code_split[0]
            type = code_split[1]
            object_id = code_split[2]
        except Exception as e:
            raise ValueError(_l.c("InvalidCode")) from e
        else:
            return URLManager.getPage(year, type, object_id)

    @staticmethod
    def getModule(year: str, type: str, object_id: str):
        _l = L(URLManager.__name__).gm("getModule")
        prefix = URLManager.origin
        middle = f"/{year}" if year != "2023" else ""
        suffix = f"/mod/{type}/view.php?id={object_id}"
        return f"{prefix}{middle}{suffix}"

    @staticmethod
    def getModuleByCodeString(module_code: str):
        _l = L(URLManager.__name__).gm("getModuleByCodeString")
        try:
            code_split = module_code.split(":")
            if len(code_split) != 7:
                raise ValueError
            year = code_split[0]
            type = code_split[5]
            object_id = code_split[6]
        except Exception as e:
            raise ValueError(_l.c("InvalidCode")) from e
        else:
            return URLManager.getModule(year, type, object_id)
