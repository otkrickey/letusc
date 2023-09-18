import asyncio
from typing import Any

import discord
from discord.ext import commands

from letusc.logger import L
from letusc.TaskManager import TaskManager
from letusc.util import env


class LetusBotClient(commands.Bot):
    _l = L()
    bot: "LetusBotClient"
    ready_event: asyncio.Event
    cogs: list[discord.CogMeta] = []

    def __new__(cls, *args: Any, **kwargs: Any) -> "LetusBotClient":
        if not hasattr(cls, "bot"):
            cls.bot = commands.Bot.__new__(cls, *args, **kwargs)
        if not hasattr(cls, "ready_event"):
            cls.ready_event = asyncio.Event()
        return cls.bot

    def __init__(self):
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__init__")
        intents = discord.Intents.default()
        intents.members = True
        commands.Bot.__init__(self, intents=intents)

    async def on_ready(self):
        _l = self._l.gm("on_ready")
        assert isinstance(self.user, discord.ClientUser)
        _l.info(f"Logged in as {self.user} (ID: {self.user.id})")
        self.ready_event.set()

    @staticmethod
    async def get_client() -> "LetusBotClient":
        _l = L(LetusBotClient.__name__).gm("get_client")
        await LetusBotClient.ready_event.wait()
        return LetusBotClient.bot

    @staticmethod
    async def wait_ready():
        _l = L(LetusBotClient.__name__).gm("wait_ready")
        await LetusBotClient.ready_event.wait()

    async def run_bot(self):
        _l = self._l.gm("run_bot")
        for cog in LetusBotClient.cogs:
            _l.info(f"Adding cog: {cog.__name__}")
            self.add_cog(cog(self))
        TaskManager.get_loop().create_task(self.wait_exit())
        await self.start(env("BOT_DISCORD_TOKEN"))

    async def wait_exit(self):
        _l = self._l.gm("wait_exit")
        exit_event = TaskManager.get_exit_event()
        await exit_event.wait()
        await self.close()
        _l.info("discord client closed")

    @staticmethod
    def add_cogMeta(cog: discord.CogMeta) -> None:
        _l = L(LetusBotClient.__name__).gm("add_cogMeta")
        LetusBotClient.cogs.append(cog)
