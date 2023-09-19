from typing import Any, Optional


class L:
    def __init__(self, name: Optional[str] = None, parent: Optional["L"] = None):
        self.name = name if name else "root"
        self.parent = parent
        self.full = f"{self.parent.full}.{self.name}" if self.parent else self.name
        full_split = []
        for o in self.full.split("."):
            if o[0].isupper():
                full_split.append(f"\033[96m{o}\033[0m")
            else:
                full_split.append(f"\033[92m{o}\033[0m")
        self.colored = ".".join(full_split)
        self.methods = []

    #### private ####
    def _s(self, length: int):
        return " " * (length - (len(self.full) + 10))

    def _hs(self, length: int, il: int = 1):
        str_len = (length - (len(self.full) + 10)) // 2
        return " " * str_len if il else " " * (str_len + 1)

    def __str__(self) -> str:
        return self.full

    def _change_name(self, name: str):
        self.__init__(name, self.parent)

    def _change_parent(self, parent: "L"):
        self.__init__(self.name, parent)

    def _add_method(self, name: str) -> None:
        self.methods.append(name)
        setattr(self, name, L(name, self))

    def _get_method(self, name: str) -> Any:
        l = getattr(self, name, None)
        return l

    def _code(self, code: str) -> str:
        return f"{self.full}:{code}"

    #### public ####
    def info(self, message):
        prefix = f"[{self._s(44)}{self.colored}]"
        print(f"[ \033[34minfo\033[0m] {prefix} {message}")

    def debug(self, message):
        prefix = f"[{self._s(44)}{self.colored}]"
        print(f"[\033[33mdebug\033[0m] {prefix} {message}")

    def error(self, message):
        prefix = f"[{self._s(44)}{self.colored}]"
        print(f"[\033[31merror\033[0m] {prefix} {message}")

    def warn(self, message):
        prefix = f"[{self._s(44)}{self.colored}]"
        print(f"[ \033[35mwarn\033[0m] {prefix} {message}")

    def i(self, name: str) -> None:
        return self._change_name(name)

    def p(self, parent: "L") -> None:
        return self._change_parent(parent)

    def am(self, name: str) -> None:
        return self._add_method(name)

    def gm(self, name: str) -> "L":
        l = self._get_method(name)
        if not isinstance(l, L):
            self.am(name)
            return self.gm(name)
        return l

    def c(self, code: str) -> str:
        return self._code(code)
