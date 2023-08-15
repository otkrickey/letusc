from src.Letus.LetusAccount import LetusAccount
from src.service.v3.middleware.fetchAccount import fetchAccount
from src.service.v3.middleware.loginAccount import loginAccount
from src.service.v3.middleware.pushAccount import pushAccount
from src.util.logger import Log


def CheckAccount(LA: LetusAccount):
    __logger = Log("Service.CheckAccount")
    try:
        fetchAccount(LA)
        loginAccount(LA)
        pushAccount(LA)
    except Exception as e:
        __logger.error(f"Code: `\33[31m{e}\33[0m`")
        __logger.error("\33[31mTerminated Service because of error\33[0m")
        raise Exception("Service:CheckAccount:Terminated")
