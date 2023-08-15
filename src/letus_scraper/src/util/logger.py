from curses.ascii import isupper
import logging
import sys

from src.util.Result import Result


class Logger:
    def __init__(self, className=None):
        level = self.__level()
        self.__handler = logging.StreamHandler()
        self.__handler.setLevel(level)

        self.__className = className
        classID = self.__className if self.__className is not None else 'anonymous'
        self.__logger = logging.getLogger(f'{classID}.{id(self)}')
        self.__logger.setLevel(level)
        for handler in self.__logger.handlers:
            self.__logger.removeHandler(handler)
        self.__logger.addHandler(self.__handler)

    def info(self, message, method):
        if self.__className is None: self.__logger.info(f'{method}(): {message}')
        else: self.__logger.info(f'{self.__className}.{method}(): {message}')

    def debug(self, message, method):
        if self.__className is None: self.__logger.debug(f'{method}(): {message}')
        else: self.__logger.debug(f'{self.__className}.{method}(): {message}')

    def error(self, e):
        self.__logger.error(e)

    def emit(self, *args):
        if len(args) == 1:
            result = args[0]
            if isinstance(result, Result):
                document = {
                    'key': result.scope,
                    'status': result.status,
                    'message': result.message,
                    'emitter': f'{self.__className}.{result.method}()' if self.__className is not None else f'{result.method}()',
                    'embed_id': self.__embed_id()
                }
                json = str(document).replace("'", '"')
                self.__logger.log(25, f'[node]: {json}')
            else: raise ValueError('Please provide a Result object')
        elif len(args) == 4:
            if isinstance(args[0], str) and isinstance(args[1], str) and isinstance(args[2], str) and isinstance(args[3], str):
                result = Result(args[0], args[1], args[2], args[3])
                self.emit(result)
            else: raise ValueError('Please provide all arguments as strings')
        else: raise ValueError('Please provide all arguments')

    def __level(self) -> int:
        args = sys.argv
        level = logging.WARNING
        try:
            if args[args.index('-l') + 1] == 'debug': level = logging.DEBUG
            elif args[args.index('-l') + 1] == 'info': level = logging.INFO
            elif args[args.index('-l') + 1] == 'node': level = 25
        except IndexError: pass
        return level

    def __embed_id(self) -> str:
        args = sys.argv
        embed_id: str
        try:
            embed_id = args[args.index('-e') + 1]
        except IndexError:
            raise IndexError('Please provide an embed ID')
        else:
            return embed_id


class Log:
    def __init__(self, obj: str, enabled: bool = True):
        self.obj = obj
        self.enabled = enabled

    def __obj(self):
        text = []
        for o in self.obj.split("."):
            if o[0].isupper():
                text.append(f"\033[96m{o}\033[0m")
            else:
                text.append(f"\033[92m{o}\033[0m")
        return ".".join(text)

    def __s(self, length: int):
        return " " * (length - (len(self.obj) + 10))

    def __hs(self, length: int, il: int = 1):
        str_len = (length - (len(self.obj) + 10)) // 2
        return " " * str_len if il else " " * (str_len + 1)

    def info(self, message):
        prefix = f"[{self.__s(44)}{self.__obj()}]"
        if self.enabled:
            print(f"[ \033[34minfo\033[0m] {prefix} {message}")

    def debug(self, message):
        prefix = f"[{self.__s(44)}{self.__obj()}]"
        if self.enabled:
            print(f"[\033[33mdebug\033[0m] {prefix} {message}")

    def error(self, message):
        prefix = f"[{self.__s(44)}{self.__obj()}]"
        if self.enabled:
            print(f"[\033[31merror\033[0m] {prefix} {message}")

    def warn(self, message):
        prefix = f"[{self.__s(44)}{self.__obj()}]"
        if self.enabled:
            print(f"[ \033[35mwarn\033[0m] {prefix} {message}")
