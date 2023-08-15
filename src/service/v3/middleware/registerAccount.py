import logging
from src.Letus.v2.LetusAccount import LetusAccount
from src.Controller.v3.LetusSessionController import LetusSessionController
from src.util.logger import Log


def registerAccount(LA: LetusAccount) -> LetusAccount:
    __logger = Log("Service.Middle.registerAccount")
    __logger.info("Register Account Start")

    if LA.email is None:
        __logger.error("Email Error")
        raise ValueError("registerAccount:EmailError")

    LSC = LetusSessionController()

    try:
        LSC.register(LA)
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
        raise Exception("registerAccount:UnknownError")
    else:
        __logger.info("Registered Account Successfully")
    return LA
