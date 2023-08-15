import logging
from src.Letus.v2.LetusAccount import LetusAccount
from src.database.v3.AccountManager import AccountManager
from src.util.logger import Log


def pushAccount(LA: LetusAccount):
    __logger = Log("Service.Middle.pushAccount")
    __logger.info("Account Uploading Start")
    AM = AccountManager(LA)

    try:
        AM.push()
    except Exception as e:
        __logger.error("Unknown Error")
        logging.error(e)
        raise ValueError("pushAccount:UnknownError")
    else:
        __logger.info("Account Uploading Success")
