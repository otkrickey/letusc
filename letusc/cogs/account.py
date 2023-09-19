import discord
from discord import SlashCommandGroup, option
from discord.ext import commands

from letusc.logger import L
from letusc.task.account_task import RegisterAccountTask
from letusc.TaskManager import TaskManager
from letusc.util import env, env_any

__all__ = [
    "Account",
]


class Account(commands.Cog):
    _l = L()

    def __init__(self, bot):
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__init__")
        self.bot = bot

    account = SlashCommandGroup(
        f"account-{env('BOT_COMMAND_SUFFIX')}"
        if env_any("BOT_COMMAND_SUFFIX")
        else "account",
        "Account commands",
    )

    @account.command(guild_ids=[1060750704626643034])
    @option(
        name="id",
        description="TUSアカウントのID",
        min_values=100000,
        max_values=999999,
        required=True,
    )
    @option(
        name="password",
        description="TUSアカウントのパスワード",
        required=True,
    )
    async def register(self, ctx: discord.ApplicationContext, id: int, password: str):
        _l = self._l.gm("register")
        task = RegisterAccountTask(
            student_id=f"{id}",
            discord_id=f"{ctx.author.id}",
            encrypted_password=password,
            username=ctx.author.name,
            discriminator=ctx.author.discriminator,
        )
        TaskManager.get_loop().create_task(task.run())

        await ctx.respond(
            "サーバーでログイン情報を確認しています。\n詳細はDMでお知らせします。\nパスワードは暗号化され、安全に保管されます。",
            ephemeral=True,
        )

    @account.command(guild_ids=[1060750704626643034])
    @option(
        name="id",
        description="TUSアカウントのID",
        min_values=100000,
        max_values=999999,
        required=True,
    )
    async def status(self, ctx: discord.ApplicationContext, id: int):
        _l = self._l.gm("status")
        await ctx.respond(
            "サーバーでログイン情報を確認しています。\n詳細はDMでお知らせします。",
            ephemeral=True,
        )
