import asyncio
from typing import Awaitable, Callable

from motor.motor_asyncio import AsyncIOMotorCollection

from letusc.logger import Log
from letusc.MongoManager import MongoManager
from letusc.task.account_task import AccountTaskBase
from letusc.task.base_task import TaskBase
from letusc.task.page_task import PageTaskBase
from letusc.TaskManager import TaskManager

__all__ = [
    "accountWatcher",
    "pageWatcher",
]


async def dbWatcher(
    collection: AsyncIOMotorCollection,
    runner_obj: Callable[[dict], Awaitable[TaskBase]],
):
    _logger = Log(f"db_watcher.{collection.name}")
    exit_event = TaskManager.get_exit_event()
    pipeline = [
        {"$match": {"operationType": "insert"}},
        {"$project": {"fullDocument": 1}},
    ]
    _logger.info(f"Watcher registered on collection: `{collection.name}`")
    async with collection.watch(pipeline, max_await_time_ms=1000) as stream:
        _logger.info(f"Watcher checking collection: `{collection.name}`")
        ## idea 1
        # async for document in stream:
        #     if exit_event.is_set():
        #         break
        #     change = document["fullDocument"]
        #     obj = await runner_obj(change)
        #     await obj.run()

        ## idea 2
        # while not exit_event.is_set():
        #     try:
        #         change = await stream.next()
        #         obj = await runner_obj(change["fullDocument"])
        #         await obj.run()
        #     except StopAsyncIteration:
        #         pass

        ## idea 3
        # while True:
        #     done, _ = await asyncio.wait(
        #         [stream.next(), exit_event.wait()], return_when=asyncio.FIRST_COMPLETED
        #     )
        #     if exit_event.is_set():
        #         break
        #     if stream in done:
        #         change = stream.result()
        #         obj = await runner_obj(change["fullDocument"])
        #         await obj.run()

        # idea 4
        while stream.alive:
            _logger.debug("Watcher checking for changes")
            change = await stream.try_next()
            if change is not None:
                obj = await runner_obj(change["fullDocument"])
                await obj.run()
            else:
                if exit_event.is_set():
                    stream.close()
                    break
                await asyncio.sleep(1)

    MongoManager.close()
    _logger.info(f"Watcher stopped on collection: `{collection.name}`")


async def accountWatcher():
    collection = MongoManager.get_collection("task", "account")
    return await dbWatcher(collection, AccountTaskBase.from_api)


async def pageWatcher():
    collection = MongoManager.get_collection("task", "page")
    return await dbWatcher(collection, PageTaskBase.from_api)
