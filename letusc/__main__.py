import socketio
from .bot import LetusBotClient
from .cogs import Account, Page, Task
from .logger import get_logger
from .sockets import SocketIOClient
from .task import TaskManager
from .util import env_bool
from .vpn import VPNManager

from .extensions.shareLink.bot import ShareLinkClient
from .extensions.shareLink.cogs import ShareLink

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

    extension_share_link_client = ShareLinkClient()
    extension_share_link_client.add_cogMeta(ShareLink)

    socketio_client = SocketIOClient.instance()

    loop = manager.get_loop()
    loop.run_until_complete(socketio_client.connect())
    # loop.create_task(accountWatcher())
    # loop.create_task(client.run_bot())
    loop.create_task(extension_share_link_client.run_bot())
    loop.create_task(socketio_client.wait())

    manager.start()


if __name__ == "__main__":
    main()
