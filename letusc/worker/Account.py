import logging

from letusc.Letus.v2.LetusAccount import LetusAccount
from letusc.logger import Log
from letusc.service import account as AccountService_old
from letusc.service import AccountV2 as AccountService
from letusc import model as Model


def Account(queue):
    __logger = Log("Worker.Account")
    __logger.info("AccountWorker started")
    while True:
        change = queue.get()

        if change is None:  # kill signal
            break

        doc = change["fullDocument"]
        try:
            match doc["task"]:
                case "account:check":
                    try:
                        discord_id = doc["Discord"]["user_id"]
                    except KeyError:
                        raise KeyError("AccountWorker:check:KeyError")
                    # LA = LetusAccount(discord_id)
                    # AccountService_old.Check(LA)
                    account = Model.Account(discord_id)
                    AccountService(account).Check()
                case "account:register":
                    # TODO: change the way to get the data
                    try:
                        # discord_id = doc["Discord"]["user_id"]
                        # user_id = doc["TUS"]["user_id"]
                        # encrypted_password = doc["TUS"]["encrypted_password"]
                        discord_id = doc["Discord"]["user_id"]
                        email = doc["TUS"]["user_id"]
                        encrypted_password = doc["TUS"]["encrypted_password"]
                    except KeyError:
                        raise KeyError("AccountWorker:register:KeyError")
                    # LA = LetusAccount(f"{discord_id}:{user_id}:{encrypted_password}")
                    # AccountService_old.Register(LA)
                    account = Model.Account(discord_id)
                    account.Letus = Model.LetusUserWithPassword(
                        email, encrypted_password
                    )
                    AccountService(account).Register()
                case "account:status":
                    try:
                        discord_id = doc["Discord"]["user_id"]
                    except KeyError:
                        raise KeyError("AccountWorker:status:KeyError")
                    LA = LetusAccount(discord_id)
                    # StatusAccount(LA)
                    AccountService_old.Status(LA)
                # case "account:delete": # TODO
                case _:
                    print(f"AccountWorker: the task `{doc['task']}` is not defined")
        except KeyError as e:
            match str(e):
                case "AccountWorker:check:KeyError":
                    __logger.error("\33[31mTerminated Task because of error\33[0m")
                case "AccountWorker:register:KeyError":
                    __logger.error("\33[31mTerminated Task because of error\33[0m")
                case _:
                    logging.error(e)
                    __logger.error("\33[31mTerminated Task because of error\33[0m")
        except Exception as e:
            match str(e):
                case "Service.Account.Check:Terminated":
                    __logger.error("\33[31mTerminated Task because of error\33[0m")
                case "Service.Account.Register:Terminated":
                    __logger.error("\33[31mTerminated Task because of error\33[0m")
                case _:
                    logging.error(e)
                    __logger.error("\33[31mTerminated Task because of error\33[0m")

        # end the task
        queue.task_done()
