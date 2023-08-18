from letusc.Letus.v2.LetusAccount import LetusAccount
from letusc.service.account import push, first_login
from letusc.logger import Log


def Register(LA: LetusAccount):
    __logger = Log("Service.Account.Register")

    try:
        first_login(LA)
        push(LA)
    except Exception as e:
        __logger.error(f"Code: `\33[31m{e}\33[0m`")
        __logger.error("\33[31mTerminated Service because of error\33[0m")
        return Exception("Service.Account.Register:Terminated")
