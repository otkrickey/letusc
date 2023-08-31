from letusc.logger import Log
from letusc.Task.Content import ContentTask


def Content(queue):
    __logger = Log("Worker.ContentWorker")
    __logger.info("ContentWorker started")
    while True:
        change = queue.get()

        if change is None:  # kill signal
            break

        task = change["fullDocument"]
        content_task = ContentTask.from_api(task)
        content_task.run()

        # end the task
        queue.task_done()
