from src.Letus.LetusAccount import LetusAccount
from src.Controller.LetusSessionController import LetusSessionController
from src.util.logger import Logger


def loginAccount(LA: LetusAccount):
    __logger = Logger()
    __logger.emit('Service:Middleware:LoginAccount:Start', '202', 'Account Checking Start', loginAccount.__name__)

    if LA.email is None:
        __logger.emit('Service:Middleware:LoginAccount:EmailError', '401', 'Email Error', loginAccount.__name__)
        exit(1)

    LSC = LetusSessionController()

    try:
        LSC.login(LA)
    except TimeoutError as e:
        if 'LetusSession:login:__login_letus:Timeout' in str(e):
            __logger.emit('Service:Middleware:LoginAccount:Timeout', '504', 'Timeout while accessing Letus Login Page', loginAccount.__name__)
            exit(1)
    except ValueError as e:
        if 'LetusSession:login:__login_letus:PasswordError' in str(e):
            __logger.emit('Service:Middleware:LoginAccount:PasswordError', '401', 'Password Error', loginAccount.__name__)
            exit(1)
    except Exception as e:
        __logger.emit('Service:Middleware:LoginAccount:Error', '500', 'Unknown Error', loginAccount.__name__)
        __logger.error(e)
        exit(1)
    else:
        __logger.emit('Service:Middleware:LoginAccount:Success', '200', 'Letus Login Success', loginAccount.__name__)

    return LA
