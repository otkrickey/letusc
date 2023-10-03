import asyncio
from datetime import datetime, timedelta

import discord
from discord.ext import commands, tasks

from letusc.tasks.account_task import RegisterAccountLoopTask, RegisterAccountTask

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
        self.cookie_ready = asyncio.Event()
        self.checkAllAccount.start()
        self.fetchAll.start()

    def cog_unload(self):
        self.fetchAll.cancel()
        self.checkAllAccount.cancel()

    @tasks.loop(minutes=int(env("CRAWLER_INTERVAL")))
    async def fetchAll(self):
        _l = self._l.gm("fetchAll")
        _l.info("task started")

        await self.bot.wait_until_ready()
        await self.cookie_ready.wait()

        await self.bot.change_presence(
            activity=discord.Activity(
                application_id=env("APP_DISCORD_CLIENT_ID"),
                name="Letusc",
                type=discord.ActivityType.playing,
                state="fetching pages",
                details="fetching all pages",
                timestamps={"start": datetime.now().timestamp()},
                assets={"large_image": "letusc-icon", "large_text": "Letusc"},
            )
        )

        collection = DBManager.get_collection("letus", "pages")
        cursor = collection.find({})

        count = 0
        async for page in cursor:
            try:
                task = await FetchPageLoopTask.create(page)
                await task.run()
                _l.info(task.code)
            except Exception as e:
                _l.error(e)
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

        await self.bot.change_presence(
            activity=discord.Activity(
                application_id=env("APP_DISCORD_CLIENT_ID"),
                name="Letusc",
                type=discord.ActivityType.playing,
                state="waiting for next fetch",
                details="waiting for next fetch",
                timestamps={
                    "end": (
                        datetime.now() + timedelta(minutes=int(env("CRAWLER_INTERVAL")))
                    ).timestamp()
                },
                assets={"large_image": "letusc-icon", "large_text": "Letusc"},
            )
        )

    @tasks.loop(hours=12)
    async def checkAllAccount(self):
        _l = self._l.gm("checkAllAccount")
        _l.info("task started")

        await self.bot.wait_until_ready()

        # wait for maintenance time to end
        maintenance_start = datetime.strptime("04:00", "%H:%M").time()
        maintenance_end = datetime.strptime("05:30", "%H:%M").time()
        while True:
            now = datetime.now().time()
            if maintenance_start <= now <= maintenance_end:
                _l.info("waiting for maintenance time to end")
                await asyncio.sleep(10 * 60)
            else:
                break

        await self.bot.change_presence(
            activity=discord.Activity(
                application_id=env("APP_DISCORD_CLIENT_ID"),
                name="Letusc",
                type=discord.ActivityType.playing,
                state="checking accounts",
                details="checking all accounts",
                timestamps={"start": datetime.now().timestamp()},
                assets={"large_image": "letusc-icon", "large_text": "Letusc"},
            )
        )

        collection = DBManager.get_collection("letus", "accounts")
        cursor = collection.find({})

        count = 0
        async for account in cursor:
            try:
                task = await RegisterAccountLoopTask.create(account)
                await task.run()
                _l.info(task.multi_id)
            except Exception as e:
                _l.error(e)
            count += 1

        self.cookie_ready.set()
