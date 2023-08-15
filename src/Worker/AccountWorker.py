import logging
from src.util.logger import Log


def AccountWorker(queue):
    __logger = Log("Worker.AccountWorker")
    __logger.info("AccountWorker started")
    while True:
        change = queue.get()

        if change is None:  # kill signal
            break

        doc = change["fullDocument"]
        __logger.info(f"AccountWorker: {doc}")

        try:
            match doc["task"]:
                case "account:check":
                    from src.Letus.LetusAccount import LetusAccount
                    from src.service.v3.checkAccount import CheckAccount

                    try:
                        discord_id = doc["Discord"]["user_id"]
                    except KeyError:
                        raise KeyError("AccountWorker:check:KeyError")
                    LA = LetusAccount(discord_id)
                    CheckAccount(LA)
                case "account:register":
                    from src.Letus.LetusAccount import LetusAccount
                    from src.service.v3.registerAccount import RegisterAccount

                    try:
                        discord_id = doc["Discord"]["user_id"]
                        user_id = doc["TUS"]["user_id"]
                        encrypted_password = doc["TUS"]["encrypted_password"]
                    except KeyError:
                        raise KeyError("AccountWorker:register:KeyError")
                    LA = LetusAccount(f"{discord_id}:{user_id}:{encrypted_password}")
                    RegisterAccount(LA)
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
                case "Service:CheckAccount:Terminated":
                    __logger.error("\33[31mTerminated Task because of error\33[0m")
                case "Service:RegisterAccount:Terminated":
                    __logger.error("\33[31mTerminated Task because of error\33[0m")
                case _:
                    logging.error(e)
                    __logger.error("\33[31mTerminated Task because of error\33[0m")

        # end the task
        queue.task_done()
