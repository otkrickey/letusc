import logging
from letusc.Letus.v2.LetusAccount import LetusAccount
from letusc.database.v3.AccountManager import AccountManager
from letusc.logger import Log


def push(LA: LetusAccount):
    __logger = Log("Service.Account.push")
    __logger.info("Start pushing account to MongoDB")

    AM = AccountManager(LA)

    try:
        AM.push()
    except Exception as e:
        __logger.error("Unknown Error")
        logging.error(e)
        raise ValueError("Service.Account.push:UnknownError")
    else:
        __logger.info("Pushed account to MongoDB successfully")
