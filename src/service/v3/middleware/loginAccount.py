import logging
from src.Letus.v2.LetusAccount import LetusAccount
from src.Controller.v3.LetusSessionController import LetusSessionController
from src.util.logger import Log, Logger


def loginAccount(LA: LetusAccount):
    __logger = Log("Service.Middle.loginAccount")
    __logger.info("Account Checking Start")

    if LA.email is None:
        __logger.error("Cannot Login without `Email`")
        raise ValueError("loginAccount:EmailError")

    LSC = LetusSessionController()

    try:
        LSC.login(LA)
    except TimeoutError as e:
        match str(e):
            case "LetusSession:login:__login_letus:Timeout":
                raise e
    except ValueError as e:
        match str(e):
            case "LetusSession:login:__login_letus:PasswordError":
                raise e
    except Exception as e:
        __logger.error("Unknown Error")
        logging.error(e)
        raise Exception("loginAccount:UnknownError")
    else:
        __logger.info("Letus Login Success")
    return LA
