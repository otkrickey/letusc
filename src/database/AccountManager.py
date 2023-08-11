from pymongo import MongoClient
from pymongo.errors import WriteError

from src.Letus.LetusAccount import LetusAccount
from src.util.logger import Logger


class AccountManager:
    def __init__(self, LA: LetusAccount):
        self.LA = LA
        self.client = MongoClient('mongodb+srv://otkrickey:Tm6Mp291LJwFIscK@letus.tcigkrt.mongodb.net/?retryWrites=true&w=majority')
        self.db = self.client['letus']
        self.collection = self.db['accounts']

        self.__logger = Logger(self.__class__.__name__)

    def check(self):
        self.__logger.emit('AccountManager:check:Start', '202', 'Checking account info', self.check.__name__)
        try:
            if not self.LA.sync:
                self.__logger.emit('AccountManager:check:SyncError', '401', 'Account not synced', self.check.__name__)
                raise ValueError('AccountManager:check:SyncError')
            if self.LA.email is None:
                self.__logger.emit('AccountManager:check:EmailError', '401', 'Email Error', self.check.__name__)
                raise ValueError('AccountManager:check:EmailError')
            if self.LA.encrypted_password is None:
                self.__logger.emit('AccountManager:check:PasswordError', '401', 'Password Error', self.check.__name__)
                raise ValueError('AccountManager:check:PasswordError')
            if (self.LA.cookie is None) or (not self.LA.cookie):
                self.__logger.emit('AccountManager:check:CookieError', '401', 'Cookie Error', self.check.__name__)
                raise ValueError('AccountManager:check:CookieError')
        except ValueError:
            self.pull()
            return self.check()
        else:
            self.__logger.emit('AccountManager:check:Success', '200', 'Account info checked', self.check.__name__)
            return

    def pull(self):
        self.__logger.emit('AccountManager:pull:Start', '202', 'Fetching account', self.pull.__name__)
        filter = {'discord_id': self.LA.discord_id}
        account = self.collection.find_one(filter)
        if account is None:
            self.__logger.emit('AccountManager:pull:NotFound', '404', 'Account not found', self.pull.__name__)
            raise ValueError('AccountManager:pull:NotFound')
        try:
            self.LA.email = account['email']
            self.LA.encrypted_password = account['encrypted_password']
            self.LA.cookie = account['cookie']
            if (self.LA.cookie is None) or (not self.LA.cookie):
                self.__logger.emit('AccountManager:pull:CookieError', '401', 'Cookie Error', self.pull.__name__)
                raise ValueError('AccountManager:pull:CookieError')
        except KeyError:
            self.__logger.emit('AccountManager:pull:KeyError', '500', 'Account could not be fetched correctly', self.pull.__name__)
            raise KeyError('AccountManager:pull:KeyError')
        else:
            self.LA.sync = True
            self.__logger.emit('AccountManager:pull:Success', '200', 'Account found', self.pull.__name__)
            return

    def push(self):
        self.__logger.emit('AccountManager:push:Start', '202', 'Pushing account', self.push.__name__)
        try:
            self.check()
            
        except ValueError as e:
            if 'AccountManager:pull:NotFound' in str(e):
                return self.register()
            else:
                raise e
        else:
            return self.update()

    def register(self):
        self.__logger.emit('AccountManager:register:Start', '202', 'Registering account', self.register.__name__)
        LAO = self.LA.export()
        try:
            self.__logger.emit('AccountManager:register:Creating', '202', 'Creating account', self.register.__name__)
            self.collection.insert_one(LAO)
        except WriteError:
            self.__logger.emit('AccountManager:register:WriteError', '409', 'Account could not be registered correctly', self.register.__name__)
            raise WriteError('AccountManager:register:WriteError')
        else:
            self.__logger.emit('AccountManager:register:Success', '200', 'Account registered', 'register')
            return

    def update(self):
        self.__logger.emit('AccountManager:update:Start', '202', 'Updating account', self.update.__name__)
        filter = {
            'discord_id': self.LA.discord_id
        }
        update = {
            '$set': {
                'email': self.LA.email,
                'encrypted_password': self.LA.encrypted_password,
                'cookie': self.LA.cookie,
            }
        }
        try:
            self.__logger.emit('AccountManager:update:Updating', '202', 'Updating account', self.update.__name__)
            self.collection.update_one(filter, update)
        except WriteError:
            self.__logger.emit('AccountManager:update:WriteError', '409', 'Account could not be updated correctly', self.update.__name__)
            raise WriteError('AccountManager:update:WriteError')
        else:
            self.__logger.emit('AccountManager:update:Success', '200', 'Account updated', self.update.__name__)
            return
