import discord
from discord import SlashCommandGroup, option
from discord.ext import commands

from ..chat import DiscordChat
from ..logger import get_logger
from ..models.code import PageCode
from ..tasks.page_task import FetchPageTask, RegisterPageTask
from ..util import env, env_any

logger = get_logger(__name__)

__all__ = [
    "Page",
]


class Page(commands.Cog):
    def __init__(self, bot_: discord.Bot):
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
        if not ctx.interaction.channel_id:
            return
        chat = await DiscordChat.getByCTX(ctx)
        await RegisterPageTask(
            f"{ctx.author.id}",
            PageCode(f"2023:course:{id}"),
        ).run(chat)
