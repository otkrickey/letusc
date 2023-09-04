from queue import Queue
from threading import Event

import discord
from discord.ext import commands

from letusc.logger import Log
from letusc.util import env

from .content import Content

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(intents=intents)


@bot.event
async def on_ready():
    _logger = Log("Discord.on_ready")
    assert isinstance(bot.user, discord.ClientUser)
    _logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")


bot.add_cog(Content(bot))


def run_bot(queue: Queue, exit_event: Event):
    _logger = Log("Discord.run_bot")
    bot.run(env("BOT_DISCORD_TOKEN"))
