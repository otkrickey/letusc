import logging
from letusc.Letus.v2.LetusAccount import LetusAccount
from letusc.Controller.v3.LetusSessionController import LetusSessionController
from letusc.logger import Log


def first_login(LA: LetusAccount) -> LetusAccount:
    __logger = Log("Service.Account.first_login")
    __logger.info("Start trying to login for the first time")

    if LA.email is None:
        __logger.error("Cannot Login without `Email`")
        raise ValueError("Service.Account.first_login:EmailError")

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
        logging.error(e)
        raise Exception("Service.Account.first_login:UnknownError")
    else:
        __logger.info("Logged in successfully")
    return LA
