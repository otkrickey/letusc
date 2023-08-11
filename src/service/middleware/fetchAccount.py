from src.database.AccountManager import AccountManager
from src.Letus.LetusAccount import LetusAccount
from src.service.middleware.loginAccount import loginAccount
from src.service.middleware.pushAccount import pushAccount
from src.util.logger import Logger


def fetchAccount(LA: LetusAccount) -> LetusAccount:
    __logger = Logger()
    __logger.emit('Service:Middleware:FetchAccount:Start', '202', 'Account Registration Start', fetchAccount.__name__)

    AM = AccountManager(LA)

    try:
        AM.check()
    except ValueError as e:
        if 'AccountManager:pull:NotFound' in str(e):
            __logger.emit('Service:Middleware:FetchAccount:NotFound', '404', 'Account Not Found', fetchAccount.__name__)
            exit(1)
        if 'AccountManager:pull:CookieError' in str(e):
            loginAccount(LA)
            pushAccount(LA)
    except KeyError as e:
        if 'AccountManager:pull:KeyError' in str(e):
            __logger.emit('Service:Middleware:FetchAccount:KeyError', '500', 'Account could not be fetched correctly', fetchAccount.__name__)
            exit(1)
    except Exception as e:
        __logger.emit('Service:Middleware:FetchAccount:Error', '500', 'Unknown Error', fetchAccount.__name__)
        __logger.info(e, fetchAccount.__name__)
        exit(1)
    else:
        __logger.emit('Service:Middleware:FetchAccount:Success', '200', 'Account Fetching Success', fetchAccount.__name__)

    return AM.LA
