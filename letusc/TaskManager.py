from threading import Thread

from pymongo import MongoClient

from letusc.logger import Log
from letusc.util.dotenv import env_bool


class TaskManager:
    __logger = Log("TaskManager")

    def __init__(self):
        self.client = MongoClient(
            "mongodb+srv://otkrickey:Tm6Mp291LJwFIscK@letus.tcigkrt.mongodb.net/?retryWrites=true&w=majority"
        )
        db_name = "task_test" if env_bool("TEST") else "task"
        self.db = self.client[db_name]
        self.stop_flag = False

    def configure(self, watcher_config, worker_config) -> None:
        __logger = Log(f"{TaskManager.__logger}.configure")
        self.watchers = []
        self.workers = []
        self.watcher_config = watcher_config
        self.worker_config = worker_config

        __logger.info("Configuring watchers and workers")
        for watcher in watcher_config:
            __thread = Thread(
                target=self.watcher,
                args=(
                    watcher["i"],
                    watcher["q"],
                ),
                daemon=True,
            )
            self.watchers.append(__thread)
        for worker in worker_config:
            __thread = Thread(target=worker["w"], args=(worker["q"],), daemon=True)
            self.workers.append(__thread)

    def start(self):
        __logger = Log(f"{TaskManager.__logger}.start")
        __logger.info("Starting watchers and workers")
        for watcher in self.watchers:
            watcher.start()

        for worker in self.workers:
            worker.start()

    def watcher(self, collection_name, task_queue):
        __logger = Log(f"{TaskManager.__logger}.watcher")
        pipeline = [
            {"$match": {"operationType": "insert"}},
            {"$project": {"fullDocument": 1}},
        ]
        __logger.info(f"Watcher registered on collection: `{collection_name}`")
        with self.db[collection_name].watch(pipeline, max_await_time_ms=1000) as stream:
            for change in stream:
                if self.stop_flag:  # stop the watcher
                    task_queue.put(None)
                    break
                task_queue.put(change)

    def stop(self):
        __logger = Log(f"{TaskManager.__logger}.stop")
        __logger.info("Stopping watchers and workers")
        self.stop_flag = True
        self.client.close()


__all__ = [
    "TaskManager",
]
