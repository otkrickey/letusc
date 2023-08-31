from dataclasses import dataclass
from letusc.model.account import Account

from letusc.logger import Log


@dataclass
class BaseTask(Account):
    __logger = Log("Task.BaseTask")
    # [must]
    task: str
    multi_id: str

    def run(self):
        raise NotImplementedError(f"{BaseTask.__logger}.run:NotImplemented")
