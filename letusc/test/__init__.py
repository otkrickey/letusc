def test():
    # test_account()
    # test_pages()
    pass


def test_account():
    from letusc.Model.Account import Account

    account = Account("2023:course:126936")
    print(account.__dict__)
    pass


def test_pages():
    from letusc.Model.Page import Page

    page = Page("2023:course:126936")
    print(page.__dict__)
    pass
