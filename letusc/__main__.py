from letusc.cogs import Account, Page, Task
from letusc.logger import L
from letusc.TaskManager import TaskManager
from letusc.util import env_bool
from letusc.VPNManager import VPNManager

from .bot import LetusBotClient


def main():
    _l = L("main").gm("async_main")

    if env_bool("VPN_ENABLED"):
        VC = VPNManager()
        VC.connect()

    # initialize managers
    manager = TaskManager()

    client = LetusBotClient()
    client.add_cogMeta(Account)
    client.add_cogMeta(Page)
    client.add_cogMeta(Task)

    loop = manager.get_loop()
    # loop.create_task(accountWatcher())
    loop.create_task(client.run_bot())

    manager.start()


if __name__ == "__main__":
    main()
