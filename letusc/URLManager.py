from letusc.logger import Log


class URLManager:
    __logger = Log("URLManager")

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
    def getPage(year: str, type: str, object_id: str):
        __logger = Log("URLManager.getPage")
        prefix = "https://letus.ed.tus.ac.jp"
        middle = f"/{year}" if year != "2023" else ""
        suffix = f"/course/view.php?id={object_id}" if type == "course" else ""
        return f"{prefix}{middle}{suffix}"
