from .bot import LetusBotClient
from .cogs import Account, Page, Task
from .logger import get_logger
from .task import TaskManager
from .util import env_bool
from .vpn import VPNManager

logger = get_logger(__name__)


def main():
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
