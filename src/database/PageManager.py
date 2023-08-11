from pymongo import MongoClient
from pymongo.errors import WriteError

from src.Letus.LetusPage import LetusPageV2
from src.util.logger import Logger


class PageManagerV2:
    def __init__(self, LP: LetusPageV2) -> None:
        self.LP = LP
        self.client = MongoClient('mongodb+srv://otkrickey:Tm6Mp291LJwFIscK@letus.tcigkrt.mongodb.net/?retryWrites=true&w=majority')
        self.db = self.client['letus']
        self.collection = self.db['pages']

        self.__logger = Logger(self.__class__.__name__)

    def check(self):
        self.__logger.emit('PageManager:check:Start', '202', 'Checking Page Info', self.check.__name__)
        try:
            if not self.LP.sync:
                self.__logger.emit('PageManager:check:SyncError', '401', 'Page not synced', self.check.__name__)
                raise ValueError('PageManager:check:SyncError')
        except ValueError:
            self.pull()
            return self.check()
        else:
            self.__logger.emit('PageManager:check:Success', '200', 'Page found', self.check.__name__)
            return

    def pull(self):
        self.__logger.emit('PageManager:pull:Start', '202', 'Fetching Page Info Start', self.pull.__name__)
        filter = {
            'key': self.LP.key,
        }
        page = self.collection.find_one(filter)
        if page is None:
            self.__logger.emit('PageManager:pull:NotFound', '404', 'Page not found', self.pull.__name__)
            raise ValueError('PageManager:pull:NotFound')
        try:
            self.LP.code = page['code']
            self.LP.accounts = page['accounts']
        except KeyError:
            self.__logger.emit('PageManager:pull:KeyError', '500', 'Page could not be fetched correctly', self.pull.__name__)
            raise KeyError('PageManager:pull:KeyError')
        else:
            self.LP.struct()
            self.LP.sync = True
            self.__logger.emit('PageManager:pull:Success', '200', 'Page found', self.pull.__name__)
            return

    def push(self):
        self.__logger.emit('PageManager:push:Start', '202', 'Fetching Page Info Start', self.push.__name__)
        try:
            self.check()
        except ValueError as e:
            if 'PageManager:pull:NotFound' in str(e):
                return self.register()
            else:
                raise e
        else:
            return self.update()

    def register(self):
        self.__logger.emit('PageManager:register:Start', '202', 'Fetching Page Info Start', self.register.__name__)
        LPO = self.LP.export()
        try:
            self.__logger.emit('PageManager:register:Creating', '202', 'Creating Page', self.register.__name__)
            self.collection.insert_one(LPO)
        except WriteError:
            self.__logger.emit('PageManager:register:WriteError', '500', 'Page could not be created', self.register.__name__)
            raise WriteError('PageManager:register:WriteError')
        else:
            self.LP.sync = True
            self.__logger.emit('PageManager:register:Success', '200', 'Page created', self.register.__name__)
            return

    def update(self):
        self.__logger.emit('PageManager:update:Start', '202', 'Fetching Page Info Start', self.update.__name__)
        filter = {
            'code': self.LP.code,
        }
        update = {
            '$set': {

                'accounts': self.LP.accounts
            }
        }
        try:
            self.__logger.emit('PageManager:update:Updating', '202', 'Updating Page', self.update.__name__)
            self.collection.update_one(filter, update)
        except WriteError:
            self.__logger.emit('PageManager:update:WriteError', '500', 'Page could not be updated', self.update.__name__)
            raise WriteError('PageManager:update:WriteError')
        else:
            self.LP.sync = True
            self.__logger.emit('PageManager:update:Success', '200', 'Page updated', self.update.__name__)
            return


# class PageManager:
#     def __init__(self, LA: LetusAccount) -> None:
#         self.LetusAccount = LA
#         self.client = MongoClient('mongodb+srv://otkrickey:Tm6Mp291LJwFIscK@letus.tcigkrt.mongodb.net/?retryWrites=true&w=majority')
#         self.db = self.client['letus']
#         self.collection = self.db['accounts']

#         self.__LetusPages = []

#         self.__logger = Logger(self.__class__.__name__)

#     def fetch(self):
#         self.__logger.emit('PageManager:fetch_pages_info:Start', '202', 'Fetching Page Info Start', self.fetch.__name__)
#         filter = {
#             'discord_id': self.LetusAccount.discord_id,
#         }
#         account = self.collection.find_one(filter)
#         if account is None:
#             self.__logger.emit('PageManager:fetch_pages_info:NotFound', '404', 'Page not found', self.fetch.__name__)
#             raise ValueError('PageManager:fetch_pages_info:NotFound')
#         try:
#             LetusPageCodes = account['pages']
#             for code in LetusPageCodes:
#                 if code: self.__LetusPages.append(LetusPageV2(code))
#         except KeyError:
#             self.__logger.emit('PageManager:fetch_pages_info:KeyError', '500', 'Page could not be fetched correctly', self.fetch.__name__)
#             raise KeyError('PageManager:fetch_pages_info:KeyError')
#         else:
#             self.__logger.emit('PageManager:fetch_pages_info:Success', '200', 'Page found', self.fetch.__name__)
#             return

#     def add_page(self, code: str):
#         self.__logger.emit('PageManager:add_page:Start', '202', 'Adding Page Start', self.add_page.__name__)
#         filter = {
#             'discord_id': self.LetusAccount.discord_id,
#         }
#         update = {
#             '$push': {
#                 'pages': code
#             }
#         }
#         self.collection.update_one(filter, update)
#         self.__logger.emit('PageManager:add_page:Success', '200', 'Page added', self.add_page.__name__)
#         return

#     def remove_page(self, code: str):
#         self.__logger.emit('PageManager:remove_page:Start', '202', 'Removing Page Start', self.remove_page.__name__)
#         filter = {
#             'discord_id': self.LetusAccount.discord_id,
#         }
#         update = {
#             '$pull': {
#                 'pages': code
#             }
#         }
#         self.collection.update_one(filter, update)
#         self.__logger.emit('PageManager:remove_page:Success', '200', 'Page removed', self.remove_page.__name__)
#         return

#     def get_page(self, code: str) -> LetusPageV2:
#         if not self.__LetusPages:
#             self.fetch()
#         for page in self.__LetusPages:
#             if page.get_code() == code:
#                 return page
#         raise ValueError('PageManager:get_page:NotFound')

#     def get_pages(self) -> list[LetusPageV2]:
#         if not self.__LetusPages:
#             self.fetch()
#         return self.__LetusPages
