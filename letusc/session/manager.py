from letusc.logger import Log
from letusc.session.automator import Automator
from letusc.util import env
from letusc import model as Model


class Manager:
    def __init__(self, account: Model.Account):
        print(f"!!!!DEBUG!!!!: {id(account)} in {repr(self)}")
        self.account = account

    def login(self):
        __logger = Log("Session.Manager.login")
        __logger.debug("Login to letus")
        if isinstance(self.account.Letus, Model.LetusUserWithCookies):
            for cookie in self.account.Letus.cookies:
                text = f'"\33[36m{cookie.name}\33[0m": "\33[36m{cookie.value}\33[0m"'
                __logger.info("Cookie found: {" + text + "}")
        else:
            __logger.warn("Cookie not found")
        self.register()

    def register(self):
        __logger = Log("Session.Manager.register")
        automator = Automator(self.account)
        automator.register()
