from .bot import LetusBotClient
from .cogs import Account, Page, Task
from .logger import L
from .task import TaskManager
from .util import env_bool
from .vpn import VPNManager


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
