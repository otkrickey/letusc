from letusc.logger import Log


def Content(queue):
    __logger = Log("Worker.ContentWorker")
    __logger.info("ContentWorker started")
    while True:
        change = queue.get()

        if change is None:  # kill signal
            break

        # do something with change
        __logger.info(f"ContentWorker: {change}")

        queue.task_done()
