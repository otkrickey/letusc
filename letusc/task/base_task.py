from dataclasses import dataclass

from letusc.logger import L

__all__ = [
    "TaskBase",
]


@dataclass
class TaskBase:
    _l = L()
    task: str

    def __post_init__(self):
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")

    @staticmethod
    async def from_api(task: dict) -> "TaskBase":
        ...

    async def run(self):
        ...
