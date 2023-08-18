import logging

from letusc.database.v3.AccountManager import AccountManager
from letusc.Letus.v2.LetusAccount import LetusAccount
from letusc.logger import Log
from letusc.service.account import login, push


def pull(LA: LetusAccount) -> LetusAccount:
    __logger = Log("Service.Account.pull")
    __logger.info("Start pulling account from MongoDB")

    AM = AccountManager(LA)

    try:
        AM.check()
    except ValueError as e:
        match str(e):
            case "AccountManager:pull:CookieError":
                login(LA)
                push(LA)
            case _:
                raise e
    except KeyError as e:
        raise e
    except Exception as e:
        logging.error(e)
        raise Exception("Service.Account.pull:UnknownError")
    else:
        __logger.info("Pulled account from MongoDB successfully")
    return AM.LA
