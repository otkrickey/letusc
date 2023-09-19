from datetime import datetime

import discord
from discord.ext import commands, tasks

from ..chat import DiscordChatThread, EmbedBuilder
from ..db import DBManager
from ..logger import L
from ..tasks.page_task import FetchPageLoopTask
from ..util import env

__all__ = [
    "Task",
]


class Task(commands.Cog):
    _l = L()

    def __init__(self, bot_: discord.Bot):
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__init__")
        self.bot = bot_
        self.fetchAll.start()

    def cog_unload(self):
        self.fetchAll.cancel()

    @tasks.loop(minutes=int(env("CRAWLER_INTERVAL")))
    async def fetchAll(self):
        _l = self._l.gm("fetchAll")
        _l.info("task started")
        collection = DBManager.get_collection("letus", "pages")
        cursor = collection.find({})

        count = 0
        async for page in cursor:
            task = await FetchPageLoopTask.create(page)
            await task.run()
            _l.info(task.code)
            count += 1

        chat = await DiscordChatThread.get(
            channel_id=int(env("DEFAULT_CHANNEL")),
            thread_id=int(env("DEFAULT_COMMAND_THREAD")),
        )

        await chat.SendFromBuilder(
            EmbedBuilder.from_json(
                "task.page.fetch_loop:Start",
                count=count,
                interval=env("CRAWLER_INTERVAL"),
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
        )
