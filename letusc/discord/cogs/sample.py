import discord
from discord.ext import commands

from letusc.logger import L

__all__ = [
    "Sample",
]


class Sample(commands.Cog):
    _l = L()

    def __init__(self, bot_: discord.Bot):
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__init__")
        self.bot = bot_

    sample = discord.SlashCommandGroup("sample", "Sample commands")

    @sample.command()
    async def hello(self, ctx: discord.ApplicationContext):
        _l = self._l.gm("hello")
        await ctx.respond("Hello, this is a slash subcommand from a cog!")

    @sample.command()
    async def ping(self, ctx: discord.ApplicationContext):
        _l = self._l.gm("ping")
        await ctx.respond("Pong!")
