from dataclasses import dataclass

from letusc.logger import Log
from letusc.Model.Account import Account
from letusc.PageParser import PageParser

from .BaseTask import BaseTask


@dataclass
class ContentTask(BaseTask):
    __logger = Log("Task.ContentTask")

    task: str
    parser: PageParser

    def __post_init__(self):
        pass

    @classmethod
    def from_api(cls, task: dict) -> "ContentTask":
        cls.__logger.info("Initializing ContentTask from API")
        account = Account(task["discord_id"])
        parser = PageParser(account, task["code"])

        action = task["task"].split(":")[1]
        match action:
            case "fetch":
                return FetchContent.from_copy(account, parser)
            case _:
                raise KeyError("Task.AccountTask.from_api:UnknownAction")

    def run(self):
        raise NotImplementedError("Task.AccountTask.run:NotImplemented")


@dataclass
class FetchContent(ContentTask):
    __logger = Log("Task.ContentTask.FetchContent")

    student_id: str
    discord_id: str

    @classmethod
    def from_copy(cls, account: Account, parser: PageParser):
        cls.__logger.info("Initializing FetchContent from copy")
        return cls(
            multi_id=account.multi_id,
            student_id=account.student_id,
            discord_id=account.discord_id,
            task="content:fetch",
            parser=parser,
        )

    def run(self):
        __logger = Log("Task.ContentTask.FetchContent.run")
        self.parser.parse()
        results = self.parser.compare()
        for result in results:
            __logger.debug(
                f"status: {result['status']}, type: {result['type']}, object_id: {repr(result['object'])}"
            )
