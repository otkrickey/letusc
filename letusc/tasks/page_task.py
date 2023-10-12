from dataclasses import dataclass, field

import discord
from discord.ui import Button, View

from ..chat import DiscordChat, DiscordChatChannel, DiscordChatThread, EmbedBuilder
from ..logger import get_logger
from ..models.code import PageCode
from ..models.page import Page
from ..parser import Parser
from ..util import env
from .base_task import TaskBase

logger = get_logger(__name__)

__all__ = [
    "RegisterPageView",
    "FetchPageView",
    "PageTaskBase",
    "FetchPageTask",
    "FetchPageLoopTask",
    "RegisterPageTask",
]


class RegisterPageView(View):
    def __init__(self, id: int, url: str | None = None):
        View.__init__(self)
        self._id = id
        if url:
            self.add_item(Button(label="Open", url=url, style=discord.ButtonStyle.link))

    @discord.ui.button(label="Register", custom_id="register")
    async def register(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ):
        logger.info("Register button clicked")
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
    def __init__(self, id: int, url: str | None = None):
        View.__init__(self)
        self._id = id
        if url:
            self.add_item(Button(label="Open", url=url, style=discord.ButtonStyle.link))

    @discord.ui.button(label="Fetch", custom_id="fetch")
    async def fetch(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction,
    ):
        logger.info("Fetch button clicked")
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
    task: str
    multi_id: str
    code: str

    @staticmethod
    async def from_api(task: dict) -> "PageTaskBase":
        action = task["task"].split(":")[1]
        match action:
            case "fetch":
                return await FetchPageTask.from_api(task)
            case "register":
                return await RegisterPageTask.from_api(task)
            case _:
                raise KeyError(logger.c("UnknownAction"))


@dataclass
class FetchPageTask(PageTaskBase):
    task: str = field(init=False, default="page:fetch")
    multi_id: str
    code: PageCode

    @classmethod
    async def from_api(cls, task: dict) -> "FetchPageTask":
        return cls(multi_id=task["discord_id"], code=PageCode.create(task["code"]))

    @classmethod
    async def create(cls, object: dict):
        page = Page(object["code"])
        page.from_api(object)
        multi_id = page.accounts[0]
        return cls(multi_id=multi_id, code=PageCode(page.code))

    async def run(self, chat: DiscordChat):
        logger.info("Fetching page")

        ctx = chat.getCTX()

        try:
            _page = await Page.pull(self.code.code)
        except Exception as e:
            if "Page.pull:NotFound" in str(e):
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
    task: str = field(init=False, default="page:fetch")
    multi_id: str
    code: PageCode

    @classmethod
    async def create(cls, object: dict):
        page = Page(object["code"])
        page.from_api(object)
        multi_id = page.accounts[0]
        return cls(multi_id=multi_id, code=PageCode(page.code))

    async def run(self):
        logger.info("Fetching page")

        try:
            _page = await Page.pull(self.code.code)
        except Exception as e:
            if "Page.pull:NotFound" in str(e):
                _page = None
            else:
                raise e

        if not _page:
            return

        parser = await Parser.from_page(_page)
        push = await parser.compare()

        if len(_page.chat) == 0:
            logger.warn("No chat bound to the page")
            pairs: list[tuple[str, str]] = [
                ("126936", "1152968855434571867"),
                ("163437", "1152969064214438030"),
                ("163553", "1152969125648412792"),
                ("164484", "1152969427390845029"),
                ("164486", "1152969614742011995"),
                ("164493", "1152969663542734879"),
                ("164503", "1152969706328834138"),
                ("164505", "1152969770560393287"),
                ("164512", "1152969809181544580"),
                ("164519", "1152969835488219276"),
                ("173694", "1152969890475548682"),
                ("173522", "1152970007119155302"),
                ("173491", "1152970071770157087"),
                ("173391", "1152970144260300891"),
                ("172880", "1152970218252009502"),
            ]
            for page_id, thread_id in pairs:
                if page_id == self.code.page_id:
                    _page.chat.update({env("DEFAULT_CHANNEL"): thread_id})
            push = True

        parser.page.chat = _page.chat
        parser.page.accounts = _page.accounts

        if push:
            await parser.page.push()
        return


@dataclass
class RegisterPageTask(PageTaskBase):
    task: str = field(init=False, default="page:register")
    multi_id: str
    code: PageCode

    @classmethod
    async def from_api(cls, task: dict) -> "RegisterPageTask":
        return cls(
            multi_id=task["discord_id"],
            code=task["code"],
        )

    async def run(self, chat: DiscordChat):
        logger.info("Registering page")

        ctx = chat.getCTX()

        try:
            _page = await Page.pull(self.code.code)
        except Exception as e:
            if "Page.pull:NotFound" in str(e):
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
