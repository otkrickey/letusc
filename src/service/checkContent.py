from src.Letus.LetusAccount import LetusAccount
from src.service.middleware.fetchAccount import fetchAccount
from src.util.logger import Logger


def CheckContent(LA: LetusAccount):
    __logger = Logger()
    LA = fetchAccount(LA)
    # PM = fetchContent(LA)
    # uploadAccount(LA)
    __logger.emit('Service:RegisterAccount:Success', '200', 'Account Registering Success', CheckContent.__name__)
