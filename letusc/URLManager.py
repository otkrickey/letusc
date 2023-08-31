from letusc.logger import Log
from letusc.util import env


class URLManager:
    __logger = Log("URLManager")
    current_year = "2021"
    origin = "https://letus.ed.tus.ac.jp"
    icon = "https://w7.pngwing.com/pngs/467/471/png-transparent-moodle-computer-icons-learning-management-system-content-management-system-others-miscellaneous-angle-text-thumbnail.png"
    thumbnail = "https://letus.ed.tus.ac.jp/theme/image.php/classic/core/1692602222/moodlelogo_grayhat"
    github = "https://github.com/ee-tus/letusc"
    discord_webhook = "https://discord.com/api/webhooks/1145189748705607810/hmMOtp0-Ym_qNvXnFYgq3lZy5rsDwkDugn8RPun3Re8VvcBgmeVP36Y2qEy2qJYGskcs"
    discord_webhook_general = "https://discord.com/api/webhooks/1146311468241920023/7YYWXjE-hezqHeXV0Ev3W-Yuqf4an5uyRQf6pIhMmmuHi7VZrlvcF87LiovloA6iIEJ6"

    @staticmethod
    def getMongo():
        user = env("MONGO_USER")
        passwd = env("MONGO_PASS")
        host = env("MONGO_HOST")
        return f"mongodb+srv://{user}:{passwd}@{host}/?retryWrites=true&w=majority"

    @staticmethod
    def getOrigin(year=current_year, omit_year=True):
        prefix = URLManager.origin
        if year != "2023" or not omit_year:
            prefix += f"/{year}"
        return prefix

    @staticmethod
    def getAuth(year=current_year, omit_year=True):
        prefix = URLManager.getOrigin(year, omit_year)
        return f"{prefix}/auth/shibboleth/index.php"

    @staticmethod
    def getPage(year: str, type: str, object_id: str):
        __logger = Log("URLManager.getPage")
        prefix = URLManager.origin
        middle = f"/{year}" if year != "2023" else ""
        suffix = f"/{type}/view.php?id={object_id}"
        return f"{prefix}{middle}{suffix}"

    @staticmethod
    def getPageByCode(page_code: str):
        __logger = Log("URLManager.getPage")
        try:
            code_split = page_code.split(":")
            if len(code_split) != 3:
                raise ValueError
            year = code_split[0]
            type = code_split[1]
            object_id = code_split[2]
        except Exception as e:
            raise ValueError("URLManager.getPage:InvalidCode") from e
        else:
            return URLManager.getPage(year, type, object_id)

    @staticmethod
    def getModule(year: str, type: str, object_id: str):
        __logger = Log("URLManager.getModule")
        prefix = URLManager.origin
        middle = f"/{year}" if year != "2023" else ""
        suffix = f"/mod/{type}/view.php?id={object_id}"
        return f"{prefix}{middle}{suffix}"

    @staticmethod
    def getModuleByCode(module_code: str):
        __logger = Log("URLManager.getModule")
        try:
            code_split = module_code.split(":")
            if len(code_split) != 7:
                raise ValueError
            year = code_split[0]
            type = code_split[5]
            object_id = code_split[6]
        except Exception as e:
            raise ValueError("URLManager.getModule:InvalidCode") from e
        else:
            return URLManager.getModule(year, type, object_id)
