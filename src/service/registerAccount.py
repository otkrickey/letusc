from src.Letus.LetusAccount import LetusAccount
from src.service.middleware.registerAccount import registerAccount
from src.service.middleware.pushAccount import pushAccount
from src.util.logger import Logger


def RegisterAccount(LA: LetusAccount):
    __logger = Logger()
    LA = registerAccount(LA)
    pushAccount(LA)
    __logger.emit('Service:RegisterAccount:Success', '200', 'Account Registering Success', RegisterAccount.__name__)
