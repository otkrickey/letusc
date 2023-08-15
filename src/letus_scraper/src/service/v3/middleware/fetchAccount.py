import logging
from src.database.v3.AccountManager import AccountManager
from src.Letus.v2.LetusAccount import LetusAccount
from src.service.v3.middleware.loginAccount import loginAccount
from src.service.v2.middleware.pushAccount import pushAccount
from src.util.logger import Log


def fetchAccount(LA: LetusAccount) -> LetusAccount:
    """fetchAccount V3

    Fetch LetusAccount from MongoDB-letus-accounts

    Parameters
    ----------
    LA : LetusAccount
        LetusAccount with only `discord_id`

    Returns
    -------
    LetusAccount
        LetusAccount with all information

    Raises
    ------
    NotFound
        Account Not Found
    KeyError
        Account could not be fetched correctly
    UnknownError
        Unknown Error
    """
    __logger = Log("Service.Middle.fetchAccount")
    __logger.info("Fetching Account from MongoDB")
    AM = AccountManager(LA)

    try:
        AM.check()
    except ValueError as e:
        match str(e):
            case "AccountManager:pull:CookieError":
                loginAccount(LA)
                pushAccount(LA)
            case _:
                raise e
    except KeyError as e:
        raise e
    except Exception as e:
        __logger.error("Unknown Error")
        logging.error(e)
        raise Exception("fetchAccount:UnknownError")
    else:
        __logger.info("Fetched Account Successfully")
    return AM.LA
