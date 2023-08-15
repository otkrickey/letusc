from src.Letus.v2.LetusAccount import LetusAccount
from src.service.v2.middleware.registerAccount import registerAccount
from src.service.v2.middleware.pushAccount import pushAccount
from src.util.logger import Logger


def RegisterAccount(LA: LetusAccount):
    __logger = Logger()
    LA = registerAccount(LA)
    pushAccount(LA)
    __logger.emit(
        "Service:RegisterAccount:Success",
        "200",
        "Account Registering Success",
        RegisterAccount.__name__,
    )
