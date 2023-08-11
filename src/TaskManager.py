import queue
from threading import Thread
from pymongo import MongoClient


class TaskManager:
    def __init__(self):
        self.client = MongoClient(
            "mongodb+srv://otkrickey:Tm6Mp291LJwFIscK@letus.tcigkrt.mongodb.net/?retryWrites=true&w=majority"
        )
        self.db = self.client["task"]
        self.stop_flag = False

    def configure(self, watcher_config, worker_config) -> None:
        self.watchers = []
        self.workers = []
        self.watcher_config = watcher_config
        self.worker_config = worker_config

        print("configuring watchers and workers")
        for watcher in watcher_config:
            __thread = Thread(
                target=self.watcher, args=(watcher["i"], watcher["q"],), daemon=True
            )
            self.watchers.append(__thread)
        for worker in worker_config:
            __thread = Thread(target=worker["w"], args=(worker["q"],), daemon=True)
            self.workers.append(__thread)

    def start(self):
        print("starting watchers and workers")
        for watcher in self.watchers:
            watcher.start()

        for worker in self.workers:
            worker.start()

    def watcher(self, collection_name, task_queue):
        pipeline = [
            {"$match": {"operationType": "insert"}},
            {"$project": {"fullDocument": 1}},
        ]
        print(f"watcher registered on collection: `{collection_name}`")
        with self.db[collection_name].watch(pipeline, max_await_time_ms=1000) as stream:
            for change in stream:
                if self.stop_flag:  # stop the watcher
                    task_queue.put(None)
                    break
                task_queue.put(change)

    def stop(self):
        print("stopping watchers and workers")
        self.stop_flag = True
        self.client.close()
