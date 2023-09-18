import asyncio
from typing import Any

import discord
from discord.ext import commands

from letusc.logger import L
from letusc.TaskManager import TaskManager
from letusc.util import env


class LetusClient(commands.Bot):
    _l = L()
    bot: "LetusClient"
    ready_event: asyncio.Event
    cogs: list[discord.CogMeta] = []

    def __new__(cls, *args: Any, **kwargs: Any) -> "LetusClient":
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
    async def get_client() -> "LetusClient":
        _l = L(LetusClient.__name__).gm("get_client")
        await LetusClient.ready_event.wait()
        return LetusClient.bot

    @staticmethod
    async def wait_ready():
        _l = L(LetusClient.__name__).gm("wait_ready")
        await LetusClient.ready_event.wait()

    async def run_bot(self):
        _l = self._l.gm("run_bot")
        for cog in LetusClient.cogs:
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
        _l = L(LetusClient.__name__).gm("add_cogMeta")
        LetusClient.cogs.append(cog)
