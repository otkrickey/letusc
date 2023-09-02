from letusc.logger import Log
from letusc.task.account_task import AccountTask


def Account(queue):
    _logger = Log("Worker.Account")
    _logger.info("AccountWorker started")
    while True:
        change = queue.get()

        if change is None:  # kill signal
            break

        task = change["fullDocument"]
        account_task = AccountTask.from_api(task)
        account_task.run()

        # end the task
        queue.task_done()
