from queue import Queue
from threading import Event

from letusc.logger import Log
from letusc.task.account_task import AccountTask
from letusc.task.content_task import ContentTask


def accountWorker(queue: Queue, exit_event: Event):
    _logger = Log("Worker.Account")
    _logger.info("AccountWorker started")
    while True:
        change = queue.get()

        if exit_event.is_set():
            break

        task = AccountTask.from_api(change)
        task.run()

        queue.task_done()

    _logger.info("AccountWorker stopped")


def contentWorker(queue: Queue, exit_event: Event):
    _logger = Log("Worker.ContentWorker")
    _logger.info("ContentWorker started")
    while True:
        change = queue.get()

        if exit_event.is_set():
            break

        task = ContentTask.from_api(change)
        task.run()

        queue.task_done()

    _logger.info("ContentWorker stopped")
