from dataclasses import dataclass

from ..logger import get_logger

logger = get_logger(__name__)

__all__ = [
    "TaskBase",
]


@dataclass
class TaskBase:
    task: str

    @staticmethod
    async def from_api(task: dict) -> "TaskBase":
        ...

    async def run(self):
        ...
