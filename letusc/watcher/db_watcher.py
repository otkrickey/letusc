from queue import Queue
from threading import Event
from pymongo import MongoClient
from pymongo.collection import Collection

from letusc.logger import Log
from letusc.URLManager import URLManager
from letusc.util import env_bool


def dbWatcher(collection: Collection, queue: Queue, exit_event: Event):
    _logger = Log(f"db_watcher.{collection.name}")
    pipeline = [
        {"$match": {"operationType": "insert"}},
        {"$project": {"fullDocument": 1}},
    ]
    _logger.info(f"Watcher registered on collection: `{collection.name}`")
    with collection.watch(pipeline, max_await_time_ms=1000) as stream:
        for change in stream:
            if exit_event.is_set():
                break
            queue.put(change["fullDocument"])

    _logger.info(f"Watcher stopped on collection: `{collection.name}`")


def accountWatcher(queue: Queue, exit_event: Event):
    db_name = "task_test" if env_bool("TEST") else "task"
    collection = MongoClient(URLManager.getMongo())[db_name]["account"]
    return dbWatcher(collection, queue, exit_event)


def contentWatcher(queue: Queue, exit_event: Event):
    db_name = "task_test" if env_bool("TEST") else "task"
    collection = MongoClient(URLManager.getMongo())[db_name]["content"]
    return dbWatcher(collection, queue, exit_event)
