from letusc.logger import Log
from letusc.task.content_task import ContentTask


def Content(queue):
    _logger = Log("Worker.ContentWorker")
    _logger.info("ContentWorker started")
    while True:
        change = queue.get()

        if change is None:  # kill signal
            break

        task = change["fullDocument"]
        content_task = ContentTask.from_api(task)
        content_task.run()

        # end the task
        queue.task_done()
