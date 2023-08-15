import sys

from src.util.logger import Logger


class ServiceManager:
    def __init__(self):
        self.__logger = Logger(self.__class__.__name__)

        args = sys.argv
        if "-s" in args:
            try:
                service = args[args.index("-s") + 1]
            except IndexError:
                self.__logger.emit(
                    "ServiceManager:IndexError",
                    "400",
                    "Please provide correct arguments",
                    self.__init__.__name__,
                )
                exit(1)
            else:
                if service == "registerAccount":
                    self.service_registerAccount()
                elif service == "checkAccount":
                    self.service_checkAccount()
                else:
                    self.__logger.emit(
                        "ServiceManager:ServiceNotFound",
                        "404",
                        "Service not found",
                        self.__init__.__name__,
                    )

    def service_checkAccount(self):
        self.__logger.emit(
            "ServiceManager:checkAccount:Start",
            "202",
            "Checking account",
            self.service_checkAccount.__name__,
        )
        try:
            discordID = sys.argv[sys.argv.index("-d") + 1]
        except IndexError:
            self.__logger.emit(
                "ServiceManager:checkAccount:IndexError",
                "400",
                "Please provide correct arguments",
                self.service_checkAccount.__name__,
            )
            exit(1)
        else:
            from src.Letus.v2.LetusAccount import LetusAccount
            from src.service.v2.checkAccount import checkAccount

            LetusAccount = LetusAccount(discordID)
            checkAccount(LetusAccount)
        exit(0)

    def service_registerAccount(self):
        self.__logger.emit(
            "ServiceManager:registerAccount:Start",
            "202",
            "Registering account",
            self.service_registerAccount.__name__,
        )
        try:
            discordID = sys.argv[sys.argv.index("-d") + 1]
            username = sys.argv[sys.argv.index("-u") + 1]
            encryptedPassword = sys.argv[sys.argv.index("-p") + 1]
        except IndexError:
            self.__logger.emit(
                "ServiceManager:registerAccount:IndexError",
                "400",
                "Please provide correct arguments",
                self.service_registerAccount.__name__,
            )
            exit(1)
        else:
            from src.Letus.v2.LetusAccount import LetusAccount
            from src.service.v2.registerAccount import RegisterAccount

            LetusAccount = LetusAccount(f"{discordID}:{username}:{encryptedPassword}")
            RegisterAccount(LetusAccount)
        exit(0)
