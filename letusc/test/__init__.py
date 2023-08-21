from letusc.logger import Log


def test():
    # test_account()
    # test_pages()
    # test_content()
    # test_module()
    # exit(0)  # debug: exit here
    pass


def test_account():
    __logger = Log("test.test_account")
    __logger.info("test_account")
    from letusc.Model.Account import Account

    account = Account("7322023")
    __logger.debug(account.__dict__)
    pass


def test_pages():
    __logger = Log("test.test_pages")
    __logger.info("test_pages")
    from letusc.Model.Page import Page

    page = Page.from_code("2023:course:126936")
    __logger.debug(page.__dict__)
    __logger.debug(type(page))
    pass


def test_content():
    __logger = Log("test.test_content")
    __logger.info("test_content")
    from letusc.Model.Content import Content

    content1 = Content.from_code("2023:course:126936:section:1078135")
    __logger.debug(content1.__dict__)
    __logger.debug(type(content1))
    content2 = Content.from_code("2023:course:126936:section:1081922")
    __logger.debug(content2.__dict__)
    __logger.debug(type(content2))
    content3 = Content.from_code("2023:course:126936:section:1078138")
    __logger.debug(content3.__dict__)
    __logger.debug(type(content3))
    pass


def test_module():
    __logger = Log("test.test_module")
    __logger.info("test_module")
    from letusc.Model.Module import Module

    module1 = Module.from_code("2023:course:126936:section:1081922:label:1277831")
    __logger.debug(module1.__dict__)
    __logger.debug(type(module1))
    module2 = Module.from_code("2023:course:126936:section:1081922:url:785895")
    __logger.debug(module2.__dict__)
    __logger.debug(type(module2))
    module3 = Module.from_code("2023:course:126936:section:1081922:page:828743")
    __logger.debug(module3.__dict__)
    __logger.debug(type(module3))
    pass
