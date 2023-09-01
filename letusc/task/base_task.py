from dataclasses import dataclass

from letusc.logger import Log
from letusc.model.account import Account


@dataclass
class BaseTask(Account):
    __logger = Log("Task.BaseTask")
    # [must]
    task: str
    multi_id: str

    def run(self):
        raise NotImplementedError(f"{BaseTask.__logger}.run:NotImplemented")
