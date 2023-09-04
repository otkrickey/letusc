from dataclasses import dataclass
from enum import Enum
from queue import Queue
from threading import Event, Thread
from typing import Callable

from letusc.logger import Log


class Keys(Enum):
    account = "account"
    content = "content"
    discord = "discord"


@dataclass
class TaskConfig:
    key: Keys
    queue: Queue
    watcher: Callable[[Queue, Event], None]
    worker: Callable[[Queue, Event], None]


class TaskManager:
    _logger = Log("TaskManager")
    _instance: "TaskManager"
    queue: dict[Keys, Queue] = {}
    watcher: dict[Keys, Thread] = {}
    worker: dict[Keys, Thread] = {}
    exit_event = Event()

    def __new__(cls) -> "TaskManager":
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def configure(self, configs: list["TaskConfig"]) -> None:
        for c in configs:
            args = (c.queue, self.exit_event)
            watcher_thread = Thread(target=c.watcher, args=args, daemon=True)
            worker_thread = Thread(target=c.worker, args=args, daemon=True)
            self.queue.update({c.key: c.queue})
            self.watcher.update({c.key: watcher_thread})
            self.worker.update({c.key: worker_thread})

    def start(self):
        _logger = Log(f"{TaskManager._logger}.start")
        _logger.info("Starting watchers and workers")
        for watcher in self.watcher.values():
            watcher.start()
        for worker in self.worker.values():
            worker.start()

    def stop(self, signum, frame):
        _logger = Log(f"{TaskManager._logger}.stop")
        _logger.info("Stopping watchers and workers")
        self.exit_event.set()

    @staticmethod
    def get_queue(key: Keys) -> Queue:
        queue = TaskManager.queue.get(key)
        assert queue is not None
        return queue


__all__ = [
    "TaskManager",
]
