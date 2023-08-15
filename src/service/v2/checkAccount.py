from src.Letus.v2.LetusAccount import LetusAccount
from src.service.v2.middleware.fetchAccount import fetchAccount
from src.service.v2.middleware.loginAccount import loginAccount
from src.service.v2.middleware.pushAccount import pushAccount
from src.util.logger import Logger


def checkAccount(LA: LetusAccount):
    __logger = Logger()
    fetchAccount(LA)
    loginAccount(LA)
    pushAccount(LA)
    __logger.emit(
        "Service:CheckAccount:Success",
        "200",
        "Account Checking Success",
        checkAccount.__name__,
    )
