from letusc.logger import Log
from letusc.MessageBuilder import MessageBuilder


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
    __logger = Log("test.test_account")
    __logger.info("test_account")
    from letusc.Model.account import Account

    account = Account("7322023")
    __logger.debug(account.__dict__)
    pass


def test_pages():
    __logger = Log("test.test_pages")
    __logger.info("test_pages")
    from letusc.Model.page import Page

    page = Page.from_code("2023:course:126936")
    __logger.debug(page.__dict__)
    __logger.debug(type(page))
    pass


def test_content():
    __logger = Log("test.test_content")
    __logger.info("test_content")
    from letusc.Model.content import Content

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
    from letusc.Model.module import Module

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


def test_parser():
    __logger = Log("test.test_parser")
    __logger.info("test_parser")
    from letusc.Model.account import Account
    from letusc.PageParser import PageParser

    account = Account("7322023")
    parser = PageParser(account, "2023:course:126936")
    parser.parse()

    # show comparison
    parser.compare()

    pass


def test_content_task():
    from letusc.Task.Content import ContentTask

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
    __logger = Log("test.test_diff_texts")
    __logger.info("test_diff_texts")
    from letusc.util.diff import diff_texts

    text1 = "EEの学生向け掲示板です（大学からの情報はCLASSで行われます）。"
    text2 = "EEの学生向け掲示板です（大学からの情報はCLASSで行われますので、CLASSも必ずご覧ください）。\n学科内の情報ですので、SNSなどでの拡散は禁止します。"
    diff = diff_texts(text1, text2)
    for line in diff:
        # __logger.debug(line)
        print(line)


def test_discord_webhook():
    __logger = Log("test.test_discord_webhook")
    __logger.info("test_discord_webhook")
    from datetime import datetime

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
