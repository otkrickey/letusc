from pymongo import MongoClient

from src.Letus.v2.LetusAccount import LetusAccount
from src.Letus.v2.LetusPage import LetusPage
from src.util.logger import Logger


class PageManager:
    def __init__(self, LA: LetusAccount) -> None:
        self.LetusAccount = LA
        self.client = MongoClient(
            "mongodb+srv://otkrickey:Tm6Mp291LJwFIscK@letus.tcigkrt.mongodb.net/?retryWrites=true&w=majority"
        )
        self.db = self.client["letus"]
        self.collection = self.db["accounts"]

        self.__LetusPages = []

        self.__logger = Logger(self.__class__.__name__)

    def fetch(self):
        self.__logger.emit(
            "PageManager:fetch_pages_info:Start",
            "202",
            "Fetching Page Info Start",
            self.fetch.__name__,
        )
        filter = {
            "discord_id": self.LetusAccount.discord_id,
        }
        account = self.collection.find_one(filter)
        if account is None:
            self.__logger.emit(
                "PageManager:fetch_pages_info:NotFound",
                "404",
                "Page not found",
                self.fetch.__name__,
            )
            raise ValueError("PageManager:fetch_pages_info:NotFound")
        try:
            LetusPageCodes = account["pages"]
            for code in LetusPageCodes:
                if code:
                    self.__LetusPages.append(LetusPage(code))
        except KeyError:
            self.__logger.emit(
                "PageManager:fetch_pages_info:KeyError",
                "500",
                "Page could not be fetched correctly",
                self.fetch.__name__,
            )
            raise KeyError("PageManager:fetch_pages_info:KeyError")
        else:
            self.__logger.emit(
                "PageManager:fetch_pages_info:Success",
                "200",
                "Page found",
                self.fetch.__name__,
            )
            return

    def add_page(self, code: str):
        self.__logger.emit(
            "PageManager:add_page:Start",
            "202",
            "Adding Page Start",
            self.add_page.__name__,
        )
        filter = {
            "discord_id": self.LetusAccount.discord_id,
        }
        update = {"$push": {"pages": code}}
        self.collection.update_one(filter, update)
        self.__logger.emit(
            "PageManager:add_page:Success", "200", "Page added", self.add_page.__name__
        )
        return

    def remove_page(self, code: str):
        self.__logger.emit(
            "PageManager:remove_page:Start",
            "202",
            "Removing Page Start",
            self.remove_page.__name__,
        )
        filter = {
            "discord_id": self.LetusAccount.discord_id,
        }
        update = {"$pull": {"pages": code}}
        self.collection.update_one(filter, update)
        self.__logger.emit(
            "PageManager:remove_page:Success",
            "200",
            "Page removed",
            self.remove_page.__name__,
        )
        return

    def get_page(self, code: str) -> LetusPage:
        if not self.__LetusPages:
            self.fetch()
        for page in self.__LetusPages:
            if page.get_code() == code:
                return page
        raise ValueError("PageManager:get_page:NotFound")

    def get_pages(self) -> list[LetusPage]:
        if not self.__LetusPages:
            self.fetch()
        return self.__LetusPages
