import json

import discord
from discord import Embed, SlashCommandGroup, option
from discord.ext import commands

from letusc.TaskManager import Keys, TaskManager


class Content(commands.Cog):
    def __init__(self, bot_: discord.Bot):
        self.bot = bot_

    content = SlashCommandGroup("content3", "Content commands")

    @content.command(guild_ids=[1060750704626643034])
    @option(
        "id",
        description="LetusページのID",
        min_values=1,
        max_values=999999,
        required=True,
    )
    async def register(self, ctx: discord.ApplicationContext, id: int):
        task = "content:register"
        content_queue = TaskManager.get_queue(Keys.content)
        task = {
            "task": task,
            "discord_id": f"{ctx.author.id}",
            "code": f"2023:course:{id}",
        }
        content_queue.put(task)
        embed = Embed(
            title="Letusページの登録",
            description=f"LetusページのID: {id} を登録しました。",
            color=0x00FF00,
        )
        embed.add_field(
            name="object", value=f"```json\n{json.dumps(task, indent=4)}```"
        )
        await ctx.respond(embed=embed, ephemeral=True)

    @content.command(guild_ids=[1060750704626643034])
    @option(
        "id",
        description="LetusページのID",
        min_values=1,
        max_values=999999,
        required=True,
    )
    async def fetch(self, ctx: discord.ApplicationContext, id: int):
        task = "content:fetch"
        content_queue = TaskManager.get_queue(Keys.content)
        task = {
            "task": task,
            "discord_id": f"{ctx.author.id}",
            "code": f"2023:course:{id}",
        }
        content_queue.put(task)
        embed = Embed(
            title="Letusページの取得",
            description=f"LetusページのID: {id} を取得しました。",
            color=0x00FF00,
        )
        embed.add_field(
            name="object", value=f"```json\n{json.dumps(task, indent=4)}```"
        )
        await ctx.respond(embed=embed, ephemeral=True)
