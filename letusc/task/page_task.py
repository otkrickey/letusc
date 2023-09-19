from dataclasses import dataclass, field

import discord
from discord.ui import Button, View

from letusc.logger import L
from letusc.modelv7.code import PageCode
from letusc.modelv7.page import Page
from letusc.PageParser import Parser
from letusc.util import env

from .base_task import TaskBase
from ..chat import (
    DiscordChat,
    DiscordChatChannel,
    DiscordChatThread,
    EmbedBuilder,
)

__all__ = [
    "RegisterPageView",
    "FetchPageView",
    "PageTaskBase",
    "FetchPageTask",
    "FetchPageLoopTask",
    "RegisterPageTask",
]


class RegisterPageView(View):
    _l = L()

    def __init__(self, id: int, url: str | None = None):
        View.__init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__init__")
        self._id = id
        if url:
            self.add_item(Button(label="Open", url=url, style=discord.ButtonStyle.link))

    @discord.ui.button(label="Register", custom_id="register")
    async def register(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ):
        _l = self._l.gm("register")
        _l.info("Register button clicked")
        await interaction.response.send_message(
            embed=EmbedBuilder.from_json("task.page.register:Start", id=self._id)
        )
        if not interaction.user:
            return
        if not interaction.channel_id:
            return
        chat = await DiscordChat.getByID(interaction.channel_id)
        await RegisterPageTask(
            str(interaction.user.id),
            PageCode(f"2023:course:{self._id}"),
        ).run(chat)


class FetchPageView(View):
    _l = L()

    def __init__(self, id: int, url: str | None = None):
        View.__init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__init__")
        self._id = id
        if url:
            self.add_item(Button(label="Open", url=url, style=discord.ButtonStyle.link))

    @discord.ui.button(label="Fetch", custom_id="fetch")
    async def fetch(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ):
        _l = self._l.gm("fetch")
        _l.info("Fetch button clicked")
        await interaction.response.send_message(
            embed=EmbedBuilder.from_json("task.page.fetch:Start", id=self._id)
        )
        if not interaction.user:
            return
        if not interaction.channel_id:
            return
        chat = await DiscordChat.getByID(interaction.channel_id)
        await FetchPageTask(
            str(interaction.user.id),
            PageCode(f"2023:course:{self._id}"),
        ).run(chat)


@dataclass
class PageTaskBase(TaskBase):
    _l = L()
    task: str
    multi_id: str
    code: str

    def __post_init__(self):
        TaskBase.__post_init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")

    @staticmethod
    async def from_api(task: dict) -> "PageTaskBase":
        _l = L(PageTaskBase.__name__).gm("from_api")
        action = task["task"].split(":")[1]
        match action:
            case "fetch":
                return await FetchPageTask.from_api(task)
            case "register":
                return await RegisterPageTask.from_api(task)
            case _:
                raise KeyError(_l.c("UnknownAction"))


@dataclass
class FetchPageTask(PageTaskBase):
    _l = L()
    task: str = field(init=False, default="page:fetch")
    multi_id: str
    code: PageCode

    def __post_init__(self):
        PageTaskBase.__post_init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")

    @classmethod
    async def from_api(cls, task: dict) -> "FetchPageTask":
        _l = L(cls.__name__).gm("from_api")
        return cls(multi_id=task["discord_id"], code=PageCode.create(task["code"]))

    @classmethod
    async def create(cls, object: dict):
        _l = L(cls.__name__).gm("create")
        page = Page(object["code"])
        page.from_api(object)
        multi_id = page.accounts[0]
        return cls(multi_id=multi_id, code=PageCode(page.code))

    async def run(self, chat: DiscordChat):
        _l = self._l.gm("run")
        _l.info("Fetching page")

        ctx = chat.getCTX()

        try:
            _page = await Page.pull(self.code.code)
        except Exception as e:
            if L("Page").gm("pull").c("NotFound") in str(e):
                _page = None
            else:
                raise e

        if not _page:
            if ctx:
                await ctx.interaction.response.send_message(
                    embed=EmbedBuilder.from_json(
                        "task.page.fetch:NotFound",
                        id=self.code.page_id,
                    ),
                    view=RegisterPageView(int(self.code.page_id), self.code.url),
                )
                return

            await chat.SendFromBuilder(
                builder=EmbedBuilder.from_json(
                    "task.page.fetch:NotFound",
                    id=self.code.page_id,
                ),
                view=RegisterPageView(int(self.code.page_id), self.code.url),
            )
            return

        if ctx:
            await ctx.interaction.response.send_message(
                embed=EmbedBuilder.from_json(
                    "task.page.fetch:Start",
                    id=self.code.page_id,
                )
            )

        parser = await Parser.from_page(_page)
        push = await parser.compare()

        parser.page.chat = _page.chat
        parser.page.accounts = _page.accounts

        for channel_id, thread_id in _page.chat.items():
            thread = await DiscordChatThread.get(int(channel_id), int(thread_id))
            await thread.SendFromBuilder(
                EmbedBuilder.from_json(
                    "task.page.fetch:OnThread",
                    title=_page.title,
                    id=self.code.page_id,
                    url=_page.url,
                )
            )

        if push:
            await parser.page.push()
        return


@dataclass
class FetchPageLoopTask(PageTaskBase):
    _l = L()
    task: str = field(init=False, default="page:fetch")
    multi_id: str
    code: PageCode

    def __post_init__(self):
        PageTaskBase.__post_init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")

    @classmethod
    async def from_api(cls, task: dict) -> "FetchPageLoopTask":
        _l = L(cls.__name__).gm("from_api")
        return cls(multi_id=task["discord_id"], code=PageCode.create(task["code"]))

    @classmethod
    async def create(cls, object: dict):
        _l = L(cls.__name__).gm("create")
        page = Page(object["code"])
        page.from_api(object)
        multi_id = page.accounts[0]
        return cls(multi_id=multi_id, code=PageCode(page.code))

    async def run(self):
        _l = self._l.gm("run")
        _l.info("Fetching page")

        try:
            _page = await Page.pull(self.code.code)
        except Exception as e:
            if L("Page").gm("pull").c("NotFound") in str(e):
                _page = None
            else:
                raise e

        if not _page:
            return

        parser = await Parser.from_page(_page)
        push = await parser.compare()

        parser.page.chat = _page.chat
        parser.page.accounts = _page.accounts

        if push:
            await parser.page.push()
        return


@dataclass
class RegisterPageTask(PageTaskBase):
    _l = L()
    task: str = field(init=False, default="page:register")
    multi_id: str
    code: PageCode

    def __post_init__(self):
        PageTaskBase.__post_init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")

    @classmethod
    async def from_api(cls, task: dict) -> "RegisterPageTask":
        return cls(
            multi_id=task["discord_id"],
            code=task["code"],
        )

    async def run(self, chat: DiscordChat):
        _l = self._l.gm("run")
        _l.info("Registering page")

        ctx = chat.getCTX()

        try:
            _page = await Page.pull(self.code.code)
        except Exception as e:
            if L("Page").gm("pull").c("NotFound") in str(e):
                _page = None
            else:
                raise e

        if _page:
            if ctx:
                await ctx.interaction.response.send_message(
                    embed=EmbedBuilder.from_json(
                        "task.page.register:AlreadyRegistered",
                        id=self.code.page_id,
                    ),
                    view=FetchPageView(int(self.code.page_id), self.code.url),
                )
                return
            await chat.SendFromBuilder(
                builder=EmbedBuilder.from_json(
                    "task.page.register:AlreadyRegistered",
                    id=self.code.page_id,
                ),
                view=FetchPageView(int(self.code.page_id), self.code.url),
            )
            return

        if ctx:
            await ctx.interaction.response.send_message(
                embed=EmbedBuilder.from_json(
                    "task.page.register:Start",
                    id=self.code.page_id,
                )
            )

        parser = await Parser.create(self.multi_id, self.code)
        channel = await DiscordChatChannel.get(int(env("DEFAULT_CHANNEL")))
        thread = await channel.chat.create_thread(
            name=f"{parser.page.title}",
            type=discord.ChannelType.public_thread,
        )
        await thread.send(content="<@&1068414672883171381>")
        push = await parser.compare()
        parser.page.bind_chat({f"{channel.chat.id}": f"{thread.id}"})
        parser.page.bind_account(f"{self.multi_id}")

        for channel_id, thread_id in parser.page.chat.items():
            thread = await DiscordChatThread.get(int(channel_id), int(thread_id))
            await thread.SendFromBuilder(
                EmbedBuilder.from_json(
                    "task.page.register:OnThread",
                    title=parser.page.title,
                    id=self.code.page_id,
                    url=parser.page.url,
                )
            )

        if push:
            await parser.page.push()
        return parser.page
