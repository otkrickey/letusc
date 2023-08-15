from src.Letus.v2.LetusAccount import LetusAccount
from src.service.v2.middleware.fetchAccount import fetchAccount
from src.util.logger import Logger


def CheckContent(LA: LetusAccount):
    __logger = Logger()
    LA = fetchAccount(LA)
    # PM = fetchContent(LA)
    # uploadAccount(LA)
    __logger.emit(
        "Service:RegisterAccount:Success",
        "200",
        "Account Registering Success",
        CheckContent.__name__,
    )
