import queue
import sys
from src.VPNManager import VPNController, VPNManager
from src.Letus.LetusAccount import LetusAccount
from src.Letus.LetusContent import LetusContentV2
from src.Letus.LetusPage import LetusPageV2
from src.ServiceManager import ServiceManager
from src.Worker.AccountWorker import AccountWorker
from src.Worker.ContentWorker import ContentWorker
from src.database.ContentManager import ContentHandlerV2, ContentManagerV2
from src.database.PageManager import PageManagerV2
from src.service.v3.checkAccount import checkAccount
from src.service.checkContent import CheckContent

from src.TaskManager import TaskManager


def test():
    # return
    LA = LetusAccount("601235188571176961")
    checkAccount(LA)
    # CheckContent(LA)
    # LP = LetusPageV2("2023:course:126936")
    # PM = PageManagerV2(LP)
    # PM.pull()
    # LP = LetusPageV2('2023:course:126936:1060750704626643034:1074363874112983092:601235188571176961')
    # PM = PageManagerV2(LP)
    # PM.push()

    # LC = LetusContentV2(LP)
    # CM = ContentManagerV2(LC)
    # CM.push()

    # print(LP.__dict__)
    # print(LP.LA.__dict__)
    # print(CM.LC.__dict__ | {'document': None})
    # print(CM.LCp.__dict__ | {'document': None})
    # for section in LC.sections:
    #     print(section.__dict__)
    #     for module in section.modules:
    #         print(module.__dict__)


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
    # SM = ServiceManager()
    TM = TaskManager()
    try:
        # test()
        main(TM)
        while True:
            pass
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        TM.stop()
        exit(0)
