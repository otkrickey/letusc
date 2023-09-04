from dataclasses import dataclass

from letusc.logger import Log
from letusc.MessageBuilder import MessageBuilder
from letusc.model.account import Account
from letusc.model.content import Content
from letusc.model.module import Module
from letusc.PageParser import PageParser

from .base_task import BaseTask


@dataclass
class ContentTask(BaseTask):
    _logger = Log("Task.ContentTask")

    task: str
    parser: PageParser

    def __post_init__(self):
        pass

    @classmethod
    def from_api(cls, task: dict) -> "ContentTask":
        cls._logger.info("Initializing ContentTask from API")
        account = Account(task["discord_id"])

        action = task["task"].split(":")[1]
        match action:
            case "fetch":
                return FetchContent.from_copy(account, task["code"])
            case "register":
                return RegisterContent.from_copy(account, task["code"])
            case _:
                raise KeyError(f"{ContentTask._logger}.from_api:UnknownAction")


@dataclass
class FetchContent(ContentTask):
    _logger = Log("Task.ContentTask.Fetch")

    student_id: str
    discord_id: str

    @classmethod
    def from_copy(cls, account: Account, code: str):
        parser = PageParser(account, code)
        return cls(
            multi_id=account.multi_id,
            student_id=account.student_id,
            discord_id=account.discord_id,
            task="content:fetch",
            parser=parser,
        )

    def run(self):
        _logger = Log(f"{FetchContent._logger}.run")
        self.parser.parse()
        contents = self.parser.compare()
        if len(contents) == 0:
            return

        _logger.info("Sending contents")

        page_title = self.parser.page.title

        ignore_ids = ["1081922", "1078139"]

        for content in contents:
            code = content["code"]
            status = content["status"]
            nc = content["new"]
            oc = content["old"]
            modules = content["modules"]
            if not isinstance(nc, Content) and not isinstance(oc, Content):
                continue

            section_title = nc.title
            content = f"{page_title}「{section_title}」(`{code}`)"
            if status == "new":
                content += "が追加されました。"
            elif status == "changed":
                content += "に変更がありました。"
            builder = MessageBuilder(
                content=content,
                thread_id="1148252344551743538",
            )
            _logger.debug("-" * 70)
            short_code = f"`{nc.content_type}:{nc.content_id}`"
            _logger.debug(f"{status}, {short_code}, 「{nc.title}」")

            fields = []

            for module in modules:
                code = module["code"]
                status = module["status"]
                nm = module["new"]
                om = module["old"]
                if not isinstance(nm, Module) and not isinstance(om, Module):
                    continue
                _logger.debug("-" * 90)
                name = f"[{nm.module_type}] {nm.title} ({status}!)"
                short_code = f"`{nm.module_type}:{nm.module_id}`"
                value = f"{nm.main or 'no description'}\n[{short_code}]({nm.module_url or nm.url})\n"
                fields.append({"name": name, "value": value, "inline": False})

                _logger.debug(f"{status}, {short_code}, 「{nm.title}」")

                for ignore_id in ignore_ids:
                    if ignore_id not in nm.code:
                        nm.push()

            for ignore_id in ignore_ids:
                if ignore_id not in nc.code:
                    nc.push()

            builder.addEmbed(
                title=f"{page_title}: 「{section_title}」 ({status}!)",
                description=nc.main or "no description",
                url=f"{nc.url}&title={nc.title}",
                timestamp=nc.timestamp,
                color=0x56D364 if status == "new" else 0xE3B341,
                fields=fields,
            )
            builder.send()

            self.parser.page.push()


@dataclass
class RegisterContent(ContentTask):
    _logger = Log("Task.ContentTask.Register")

    student_id: str
    discord_id: str

    parser: PageParser

    @classmethod
    def from_copy(cls, account: Account, code: str):
        return cls(
            multi_id=account.multi_id,
            student_id=account.student_id,
            discord_id=account.discord_id,
            task="content:fetch",
            parser=PageParser(account, code),
        )

    def run(self):
        _logger = Log(f"{RegisterContent._logger}.run")
        if self.parser.page_old:
            _logger.warn("Page already exists")
            return
        self.parser.parse()
        contents = self.parser.compare()
        if len(contents) == 0:
            return

        _logger.info("Registering contents (no notification)")

        ignore_ids = ["1081922", "1078139"]

        for content in contents:
            nc = content["new"]
            for module in content["modules"]:
                nm = module["new"]
                for ignore_id in ignore_ids:
                    if ignore_id not in nm.code:
                        nm.push()
            for ignore_id in ignore_ids:
                if ignore_id not in nc.code:
                    nc.push()
        self.parser.page.push()
