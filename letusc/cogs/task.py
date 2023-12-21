import asyncio
from datetime import datetime, timedelta

import discord
from discord.ext import commands, tasks

from letusc.tasks.account_task import RegisterAccountLoopTask

from ..chat import DiscordChatThread, EmbedBuilder
from ..db import DBManager
from ..logger import get_logger
from ..tasks.page_task import FetchPageLoopTask
from ..util import env

logger = get_logger(__name__)

__all__ = [
    "Task",
]


class Task(commands.Cog):
    def __init__(self, bot_: discord.Bot):
        self.bot = bot_
        self.cookie_ready = asyncio.Event()
        self.fetchAll.start()
        self.checkAllAccount.start()
        self.maintainThread.start()

    def cog_unload(self):
        self.fetchAll.cancel()
        self.checkAllAccount.cancel()
        self.maintainThread.cancel()

    @tasks.loop(minutes=int(env("CRAWLER_INTERVAL")))
    async def fetchAll(self):
        logger.info("task started")

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
                logger.info(task.code)
            except Exception as e:
                logger.error(e)
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
        logger.info("task started")

        await self.bot.wait_until_ready()

        # wait for maintenance time to end
        maintenance_start = datetime.strptime("04:00", "%H:%M").time()
        maintenance_end = datetime.strptime("05:30", "%H:%M").time()
        while True:
            now = datetime.now().time()
            if maintenance_start <= now <= maintenance_end:
                logger.info("waiting for maintenance time to end")
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
                logger.info(task.multi_id)
            except Exception as e:
                logger.error(e)
            count += 1

        self.cookie_ready.set()

    @tasks.loop(hours=23)
    async def maintainThread(self):
        logger.info("task started")

        await self.bot.wait_until_ready()

        collection = DBManager.get_collection("letus", "pages")
        cursor = collection.find({}, {"_id": 0, "chat": 1})

        async for page_object in cursor:
            try:
                # like this
                # page_object: dict = {'chat': {'1145206805849452634': '1152968855434571867'}}
                for channel_id, thread_id in page_object["chat"].items():
                    chat = await DiscordChatThread.get(
                        channel_id=int(channel_id),
                        thread_id=int(thread_id),
                    )
                    await chat.SendFromBuilder(
                        EmbedBuilder.from_json(
                            "task.thread.maintain:Start",
                            date=datetime.now().strftime("%Y年%m月%d日"),
                            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        ),
                        silent=True,
                    )
            except Exception as e:
                logger.error(e)
