from letusc.cogs import Account, Page, Task
from letusc.logger import L
from letusc.TaskManager import TaskManager
from letusc.test.post_test import async_post_test
from letusc.test.test import test
from letusc.util import env_bool
from letusc.VPNManager import VPNManager

from .bot import LetusBotClient


def async_main():
    _l = L("main").gm("async_main")
    is_test = env_bool("TEST")
    if is_test:
        test()
    else:
        VC = VPNManager()
        VC.connect()

    # initialize managers
    manager = TaskManager()
    client = LetusBotClient()
    loop = manager.get_loop()

    client.add_cogMeta(Account)
    client.add_cogMeta(Page)
    client.add_cogMeta(Task)

    # loop.create_task(accountWatcher())
    loop.create_task(client.run_bot())

    if is_test:
        loop.create_task(async_post_test())

    manager.start()


if __name__ == "__main__":
    async_main()
