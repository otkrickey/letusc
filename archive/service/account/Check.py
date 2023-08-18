from letusc.Letus.v2.LetusAccount import LetusAccount
from letusc.logger import Log
from letusc.service.account import login, pull, push


def Check(LA: LetusAccount):
    __logger = Log("Service.Account.Check")

    try:
        pull(LA)
        login(LA)
        push(LA)
    except Exception as e:
        __logger.error(f"Code: `\33[31m{e}\33[0m`")
        __logger.error("\33[31mTerminated Service because of error\33[0m")
        raise Exception("Service.Account.Check:Terminated")
