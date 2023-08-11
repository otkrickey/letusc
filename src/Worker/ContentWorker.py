def ContentWorker(queue):
    print("ContentWorker started")
    while True:
        change = queue.get()

        if change is None:  # kill signal
            break

        # do something with change
        print(f"ContentWorker: {change}")

        queue.task_done()