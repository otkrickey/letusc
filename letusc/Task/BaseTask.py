from dataclasses import dataclass
from letusc.Model.account import Account

from letusc.logger import Log


@dataclass
class BaseTask(Account):
    __logger = Log("Task.BaseTask")
    # [must]
    task: str
    multi_id: str
