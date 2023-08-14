from src.util.logger import Log


def AccountWorker(queue):
    __logger = Log("AccountWorker")
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
                    from src.service.v3.checkAccount import checkAccount

                    discord_id = doc["Discord"]["user_id"]
                    LA = LetusAccount(discord_id)
                    checkAccount(LA)
                case "account:register":
                    from src.Letus.LetusAccount import LetusAccount
                    from src.service.v3.middleware.registerAccount import registerAccount

                    discord_id = doc["Discord"]["user_id"]
                    user_id = doc["TUS"]["user_id"]
                    encrypted_password = doc["TUS"]["encrypted_password"]
                    LA = LetusAccount(f"{discord_id}:{user_id}:{encrypted_password}")
                    registerAccount(LA)
                # case "account:delete": # TODO
                case _:
                    print(f"AccountWorker: the task `{doc['task']}` is not defined")
        except Exception as e:
            match str(e):
                case "Service:checkAccount:Terminated":
                    __logger.error("\33[31mTerminated Task because of error\33[0m")
                case _:
                    # logging.error(e)
                    __logger.error("\33[31mTerminated Task because of error\33[0m")
                    raise e

        # end the task
        queue.task_done()
