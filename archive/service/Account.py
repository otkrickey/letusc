import logging
from letusc.logger import Log
from letusc import Model
from letusc import Session


class Account:
    def __init__(self, account: Model.Account):
        self.account = account

    # middleware function
    def first_login(self):
        __logger = Log("Service.Account.first_login")
        session = Session.Manager(self.account)
        try:
            session.register()
        except TimeoutError as e:
            match str(e):
                case "Session.Automator.login_letus:Timeout":
                    raise e
        except ValueError as e:
            match str(e):
                case "Session.Automator.login_letus:PasswordError":
                    raise e
        except Exception as e:
            logging.error(e)
            raise Exception("Service.Account.first_login:UnknownError")
        else:
            __logger.info("Logged in successfully")

    def login(self):
        __logger = Log("Service.Account.login")
        session = Session.Manager(self.account)
        try:
            session.login()
        except TimeoutError as e:
            match str(e):
                case "Session.Automator.login_letus:Timeout":
                    raise e
        except ValueError as e:
            match str(e):
                case "Session.Automator.login_letus:PasswordError":
                    raise e
        except Exception as e:
            logging.error(e)
            raise Exception("Service.Account.login:UnknownError")
        else:
            __logger.info("Logged in successfully")

    def pull(self):
        __logger = Log("Service.Account.pull")
        __logger.info("Start pulling account from MongoDB")
        try:
            self.account.check()
        except ValueError as e:
            match str(e):
                case "Model.Account.check:CookieError":
                    self.login()
                    self.push()
                case _:
                    raise e
        except KeyError as e:
            raise e
        except Exception as e:
            logging.error(e)
            raise Exception("Service.Account.pull:UnknownError")
        else:
            __logger.info("Pulled account from MongoDB successfully")

    def push(self):
        __logger = Log("Service.Account.push")
        __logger.info("Start pushing account to MongoDB")
        try:
            self.account.push()
        except Exception as e:
            __logger.error("Unknown Error")
            logging.error(e)
            raise ValueError("Service.Account.push:UnknownError")
        else:
            __logger.info("Pushed account to MongoDB successfully")

    # main function
    def Check(self):
        __logger = Log("Service.Account.Check")
        try:
            self.pull()
            self.login()
            self.push()
        except Exception as e:
            __logger.error(f"Code: `\33[31m{e}\33[0m`")
            __logger.error("\33[31mTerminated Service because of error\33[0m")
            raise Exception("Service.Account.Check:Terminated")

    def Register(self):
        __logger = Log("Service.Account.Register")
        try:
            self.first_login()
            self.push()
        except Exception as e:
            __logger.error(f"Code: `\33[31m{e}\33[0m`")
            __logger.error("\33[31mTerminated Service because of error\33[0m")
            return Exception("Service.Account.Register:Terminated")

    def Status(self):
        __logger = Log("Service.Account.Status")
        # TODO: check status account
        # try:
        #     statusAccount
