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
