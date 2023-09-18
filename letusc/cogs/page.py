import discord
from discord import SlashCommandGroup, option
from discord.ext import commands

from letusc.logger import L
from letusc.modelv7.code import PageCode
from letusc.task.discord_task import DiscordChat
from letusc.task.page_task import FetchPageTask, RegisterPageTask
from letusc.util import env, env_any

__all__ = [
    "Page",
]


class Page(commands.Cog):
    _l = L()

    def __init__(self, bot_: discord.Bot):
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__init__")
        self.bot = bot_

    page = SlashCommandGroup(
        f"page-{env('BOT_COMMAND_SUFFIX')}"
        if env_any("BOT_COMMAND_SUFFIX")
        else "page",
        "Page Commands",
    )

    @page.command(guild_ids=[1060750704626643034])
    @option(
        "id",
        description="LetusページのID",
        min_values=1,
        max_values=999999,
        required=True,
    )
    async def fetch(self, ctx: discord.ApplicationContext, id: int):
        _l = self._l.gm("fetch")
        if not ctx.interaction.channel_id:
            return
        chat = await DiscordChat.getByCTX(ctx)
        await FetchPageTask(
            multi_id=f"{ctx.author.id}",
            code=PageCode(f"2023:course:{id}"),
        ).run(chat)

    @page.command(guild_ids=[1060750704626643034])
    @option(
        "id",
        description="LetusページのID",
        min_values=1,
        max_values=999999,
        required=True,
    )
    async def register(self, ctx: discord.ApplicationContext, id: int):
        _l = self._l.gm("register")
        if not ctx.interaction.channel_id:
            return
        chat = await DiscordChat.getByCTX(ctx)
        await RegisterPageTask(
            f"{ctx.author.id}",
            PageCode(f"2023:course:{id}"),
        ).run(chat)
