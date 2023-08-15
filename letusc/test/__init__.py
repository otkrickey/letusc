def test():
    test_Model()
    pass


def test_Model():
    from letusc.model import Account

    account = Account(multi_id="7322023")

    print(account.__dict__)
