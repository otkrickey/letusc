import logging
from letusc.Controller.v3.LetusSessionController import LetusSessionController
from letusc.Letus.v2.LetusAccount import LetusAccount
from letusc.logger import Log


def login(LA: LetusAccount):
    __logger = Log("Service.Account.login")
    __logger.info("Start checking Letus Account by trying to login")

    if LA.email is None:
        __logger.error("Cannot Login without `Email`")
        raise ValueError("Service.Account.login:EmailError")

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
        logging.error(e)
        raise Exception("Service.Account.login:UnknownError")
    else:
        __logger.info("Logged in successfully")
    return LA
