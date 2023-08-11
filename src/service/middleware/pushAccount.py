from src.Letus.LetusAccount import LetusAccount
from src.database.AccountManager import AccountManager
from src.util.logger import Logger


def pushAccount(LA: LetusAccount):
    __logger = Logger()
    __logger.emit('Service:Middleware:PushAccount:Start', '202', 'Account Uploading Start', pushAccount.__name__)

    AM = AccountManager(LA)
    try:
        __logger.emit('Service:Middleware:PushAccount:Upload:Start', '202', 'Account Uploading Start', pushAccount.__name__)
        AM.push()
    except Exception as e:
        __logger.emit('Service:Middleware:PushAccount:Upload:Error', '500', 'Unknown Error', pushAccount.__name__)
        __logger.info(e, pushAccount.__name__)
        exit(1)
    else:
        __logger.emit('Service:Middleware:PushAccount:Upload:Success', '200', 'Account Uploading Success', pushAccount.__name__)
        __logger.emit('Service:Middleware:PushAccount:Success', '200', 'Account Uploading Success', pushAccount.__name__)
