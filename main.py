import queue

from src.TaskManager import TaskManager
from src.test import test
from src.VPNManager import VPNController
from src.Worker.AccountWorker import AccountWorker
from src.Worker.ContentWorker import ContentWorker


def main(TM: TaskManager):
    VC = VPNController()
    VC.connect()

    AccountTaskQueue = queue.Queue()
    ContentTaskQueue = queue.Queue()
    watcher_config = [
        # {i: watcher id, q: task queue}
        {"i": "account", "q": AccountTaskQueue},
        {"i": "content", "q": ContentTaskQueue},
    ]
    worker_config = [
        # {w: worker function, q: task queue}
        {"w": AccountWorker, "q": AccountTaskQueue},
        {"w": ContentWorker, "q": ContentTaskQueue},
    ]
    TM.configure(watcher_config, worker_config)
    TM.start()


"""
/home/otkrickey/otkrickey/letus_bot/letus-scraper/.venv/bin/python3.11 /home/otkrickey/otkrickey/letus_bot/letus-scraper/main.py -l info -e 1
"""

if __name__ == "__main__":
    TM = TaskManager()
    try:
        test()
        main(TM)
        while True:
            pass
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        TM.stop()
        exit(0)
