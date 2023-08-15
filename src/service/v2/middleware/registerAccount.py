from src.Letus.v2.LetusAccount import LetusAccount
from src.Controller.v2.LetusSessionController import LetusSessionController
from src.util.logger import Logger


def registerAccount(LA: LetusAccount) -> LetusAccount:
    __logger = Logger()
    __logger.emit(
        "Service:Middleware:Register:Start",
        "202",
        "Account Checking Start",
        registerAccount.__name__,
    )

    if LA.email is None:
        __logger.emit(
            "Service:Middleware:Register:EmailError",
            "401",
            "Email Error",
            registerAccount.__name__,
        )
        exit(1)

    LSC = LetusSessionController()

    try:
        LSC.register(LA)
    except TimeoutError as e:
        if "LetusSession:login:__login_letus:Timeout" in str(e):
            __logger.emit(
                "Service:Middleware:Register:Timeout",
                "504",
                "Timeout while accessing Letus Login Page",
                registerAccount.__name__,
            )
            exit(1)
    except ValueError as e:
        if "LetusSession:login:__login_letus:PasswordError" in str(e):
            __logger.emit(
                "Service:Middleware:Register:PasswordError",
                "401",
                "Password Error",
                registerAccount.__name__,
            )
            exit(1)
    except Exception as e:
        __logger.emit(
            "Service:Middleware:Register:Error",
            "500",
            "Unknown Error",
            registerAccount.__name__,
        )
        __logger.error(e)
        exit(1)
    else:
        __logger.emit(
            "Service:Middleware:Register:Success",
            "200",
            "Letus Login Success",
            registerAccount.__name__,
        )

    return LA
