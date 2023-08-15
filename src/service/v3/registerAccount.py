from src.Letus.LetusAccount import LetusAccount
from src.service.v3.middleware.registerAccount import registerAccount
from src.service.middleware.pushAccount import pushAccount
from src.util.logger import Log


def RegisterAccount(LA: LetusAccount):
    __logger = Log("Service.RegisterAccount")

    try:
        LA = registerAccount(LA)
        pushAccount(LA)
    except Exception as e:
        __logger.error(f"Code: `\33[31m{e}\33[0m`")
        __logger.error("\33[31mTerminated Service because of error\33[0m")
        return Exception("Service:RegisterAccount:Terminated")
