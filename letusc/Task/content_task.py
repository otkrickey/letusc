from dataclasses import dataclass

from letusc.logger import Log
from letusc.MessageBuilder import MessageBuilder
from letusc.Model.account import Account
from letusc.Model.content import Content
from letusc.Model.module import Module
from letusc.PageParser import PageParser

from .base_task import BaseTask


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
        contents = self.parser.compare()
        if len(contents) == 0:
            return

        page_title = self.parser.page.title

        ignore_ids = ["1081922", "1078139"]

        for content in contents:
            code = content["code"]
            status = content["status"]
            type = content["type"]
            new = content["new"]
            old = content["old"]
            modules = content["modules"]
            if not isinstance(new, Content) or not isinstance(old, Content):
                continue

            content = f"{page_title}「{new.title}」(`{code}`)"
            if status == "new":
                content += "が追加されました。"
            elif status == "changed":
                content += "に変更がありました。"
            builder = MessageBuilder(
                content=content,
                thread_id="1146305009076686868",
            )
            __logger.debug("-" * 70)
            short_code = f"`{new.content_type}:{new.content_id}`"
            __logger.debug(f"{status}, {short_code}, 「{new.title}」")

            fields = []

            for module in modules:
                code = module["code"]
                status = module["status"]
                type = module["type"]
                new = module["new"]
                old = module["old"]
                if not isinstance(new, Module) or not isinstance(old, Module):
                    continue
                __logger.debug("-" * 90)
                name = f"[{new.module_type}] {new.title} ({status}!)"
                short_code = f"`{new.module_type}:{new.module_id}`"
                value = f"{new.main or 'no description'}\n[{short_code}]({new.module_url or new.url})\n"
                fields.append({"name": name, "value": value, "inline": False})

                __logger.debug(f"{status}, {short_code}, 「{new.title}」")

                for ignore_id in ignore_ids:
                    if ignore_id not in new.code:
                        new.push()

            for ignore_id in ignore_ids:
                if ignore_id not in new.code:
                    new.push()

            builder.addEmbed(
                title=f"{page_title}: 「{new.title}」 ({status}!)",
                description=new.main or "no description",
                url=f"{new.url}&title={new.title}",
                timestamp=new.timestamp,
                color=0x56D364 if status == "new" else 0xE3B341,
                fields=fields,
            )
            builder.send()
