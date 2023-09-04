import signal
from queue import Queue

from letusc.discord import run_bot
from letusc.TaskManager import Keys, TaskConfig, TaskManager
from letusc.test import test
from letusc.test.post_test import post_test
from letusc.util import env_bool
from letusc.VPNManager import VPNController
from letusc.watcher.db_watcher import accountWatcher, contentWatcher
from letusc.worker.db_worker import accountWorker, contentWorker
from letusc.worker.discord_worker import discordWorker


def main(TM: TaskManager):
    is_test = env_bool("TEST")
    if is_test:
        test()
    else:
        VC = VPNController()
        VC.connect()

    task_configs = [
        TaskConfig(Keys.account, Queue(), accountWatcher, accountWorker),
        TaskConfig(Keys.content, Queue(), contentWatcher, contentWorker),
        TaskConfig(Keys.discord, Queue(), run_bot, discordWorker),
    ]
    TM.configure(task_configs)
    TM.start()

    if is_test:
        post_test()


if __name__ == "__main__":
    TM = TaskManager()
    try:
        main(TM)
        while True:
            pass
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        signal.signal(signal.SIGINT, TM.stop)
        exit(0)
