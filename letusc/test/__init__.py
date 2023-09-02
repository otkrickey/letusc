from letusc.logger import Log


def test():
    # test_account()
    # test_pages()
    # test_content()
    # test_module()
    # test_parser()
    # test_content_task()
    # test_diff_texts()
    # test_discord_webhook()
    # exit(0)  # debug: exit here
    pass


def test_account():
    _logger = Log("test.test_account")
    _logger.info("test_account")
    from letusc.model.account import Account

    account = Account("7322023")
    _logger.debug(account.__dict__)
    pass


def test_pages():
    _logger = Log("test.test_pages")
    _logger.info("test_pages")
    from letusc.model.page import Page

    page = Page.from_code("2023:course:126936")
    _logger.debug(page.__dict__)
    _logger.debug(type(page))
    pass


def test_content():
    _logger = Log("test.test_content")
    _logger.info("test_content")
    from letusc.model.content import Content

    content1 = Content.from_code("2023:course:126936:section:1078135")
    _logger.debug(content1.__dict__)
    _logger.debug(type(content1))
    content2 = Content.from_code("2023:course:126936:section:1081922")
    _logger.debug(content2.__dict__)
    _logger.debug(type(content2))
    content3 = Content.from_code("2023:course:126936:section:1078138")
    _logger.debug(content3.__dict__)
    _logger.debug(type(content3))
    pass


def test_module():
    _logger = Log("test.test_module")
    _logger.info("test_module")
    from letusc.model.module import Module

    module1 = Module.from_code("2023:course:126936:section:1081922:label:1277831")
    _logger.debug(module1.__dict__)
    _logger.debug(type(module1))
    module2 = Module.from_code("2023:course:126936:section:1081922:url:785895")
    _logger.debug(module2.__dict__)
    _logger.debug(type(module2))
    module3 = Module.from_code("2023:course:126936:section:1081922:page:828743")
    _logger.debug(module3.__dict__)
    _logger.debug(type(module3))
    pass


def test_parser():
    _logger = Log("test.test_parser")
    _logger.info("test_parser")
    from letusc.model.account import Account
    from letusc.PageParser import PageParser

    account = Account("7322023")
    parser = PageParser(account, "2023:course:126936")
    parser.parse()

    # show comparison
    parser.compare()

    pass


def test_content_task():
    from letusc.task.content_task import ContentTask

    task = ContentTask.from_api(
        {
            "task": "content:fetch",
            "discord_id": "601235188571176961",
            "code": "2023:course:126936",
        }
    )
    task.run()
    pass


def test_diff_texts():
    _logger = Log("test.test_diff_texts")
    _logger.info("test_diff_texts")
    from letusc.util import diff_texts

    text1 = "EEの学生向け掲示板です（大学からの情報はCLASSで行われます）。"
    text2 = "EEの学生向け掲示板です（大学からの情報はCLASSで行われますので、CLASSも必ずご覧ください）。\n学科内の情報ですので、SNSなどでの拡散は禁止します。"
    diff = diff_texts(text1, text2)
    for line in diff:
        # _logger.debug(line)
        print(line)


def test_discord_webhook():
    _logger = Log("test.test_discord_webhook")
    _logger.info("test_discord_webhook")
    from datetime import datetime

    from letusc.MessageBuilder import MessageBuilder

    THREAD_ID = 1145207293105942668
    builder = MessageBuilder(thread_id=str(THREAD_ID))
    builder.addEmbed(
        title="「EE 共通掲示板」における変更通知 `course:126936`",
        description="section:1081922",
        url="https://letus.ed.tus.ac.jp/course/view.php?id=126936",
        timestamp=datetime.now(),
        color=0x00FFFF,
    )
    builder.addEmbed(
        title="PC・IT環境設定について",
        description="no change",
        url="https://letus.ed.tus.ac.jp/mod/page/view.php?id=828743",
        timestamp=datetime.now(),
        color=0x00FFFF,
    )
    builder.addEmbed(
        title="「学園生活」の電子化について",
        description="これまで冊子で配布していました。「学園生活」について、電子版に変わりました。\n\r\n証明証や奨学金などの手続方法や、生活サポートなど、常に最新の情報が公開されます。\n\r\n新入生は必ずご一読ください。",
        url="https://letus.ed.tus.ac.jp/mod/url/view.php?id=785895",
        timestamp=datetime.now(),
        color=0x00FFFF,
    )
    builder.send()
