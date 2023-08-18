import queue

from letusc import Worker
from letusc.TaskManager import TaskManager
from letusc.test import test
from letusc.VPNManager import VPNController


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
        {"w": Worker.Account, "q": AccountTaskQueue},
        {"w": Worker.Content, "q": ContentTaskQueue},
    ]
    TM.configure(watcher_config, worker_config)
    TM.start()


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
