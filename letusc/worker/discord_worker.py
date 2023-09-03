from queue import Queue
from threading import Event

from letusc.logger import Log


def discordWorker(queue: Queue, exit_event: Event):
    _logger = Log("Worker.DiscordWorker")
    _logger.info("DiscordWorker started")
    while True:
        change = queue.get()

        if exit_event.is_set():
            break

        _logger.debug(f"received: {change.__name__}")
        _logger.debug(f"queue size: {queue.qsize()}")
        change()

        # end the task
        queue.task_done()
