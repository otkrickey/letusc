import json

from letusc.logger import L
from letusc.util import env


async def async_post_test():
    _l = L("async_post_test")
    from letusc.discord import LetusClient

    await LetusClient.wait_ready()

    # \\ test function here //
    # await test_send_message()
    await test_model_v7()


async def test_send_message():
    _l = L("test_send_message")
    # from letusc.task.discord_task import ChatChannel_

    # await ChatChannel_(
    #     channel_id=1145206805849452634,
    # ).SendMessage("test")


async def test_model_v7():
    _l = L("test_model_v7")
    # await test_model_v7_account(_l)
    # await test_model_v7_page(_l)
    # await test_parser()
    pass


async def test_model_v7_account(_l: L):
    _l = _l.gm("account")

    from letusc.modelv7.account import NewAccount
    from letusc.modelv7.cookie import Cookie

    new_account = NewAccount.create(
        student_id=env("TUS_ID"),
        discord_id=env("DISCORD_ID"),
        encrypted_password=env("VPN_PASS"),
        username="otkrickey",
        discriminator="otkrickey",
    )
    new_account.Letus.cookies = [
        Cookie(
            name="MoodleSession2023",
            value="tfp9ctrs0dgoa986pkt7citao4",
            year="2023",
        )
    ]
    await new_account.push()


async def test_model_v7_page(_l: L):
    _l = _l.gm("page")
    from letusc.modelv7.account import Account
    from letusc.modelv7.page import Page

    account = await Account.pull(env("TUS_ID"))
    page = await Page.pull("2023:course:126936")
    cookie = account.get_cookie(page.year)
    _l.debug("page:")
    print(page.__dict__)
    print(str(json.dumps(page.to_api(), indent=4)))

    await page.get(cookie)


async def test_parser():
    _l = L("test_parser")

    from letusc.PageParser import Parser

    # parser = await Parser.create(env("TUS_ID"), "2023:course:126936")
    # parser = await Parser.create(env("TUS_ID"), "2023:course:169670")

    # await parser._compare()

    # assert parser._page
    # for content in parser.page.contents:
    #     _l.debug(f"content: {content}")
    # for content in parser._page.contents:
    #     _l.debug(f"content: {content.hash}")

    # for k, v in parser.page.contents.items():
    #     if k in parser._page.contents.keys():
    #         if v.hash == parser._page.contents[k].hash:
    #             _l.debug(f"content: {k} has not changed.")
    #         else:
    #             _l.debug(f"content: {k} has changed.")
    #     else:
    #         _l.debug(f"content: {k} is new.")

    # for k in parser._page.contents:
    #     if k not in parser.page.contents:
    #         _l.debug(f"content: {k} has been removed.")

    # for content in parser.page.contents.values():
    #     await content._update()
    #     for module in content.modules.values():
    #         await module._update()
    # await parser.page._update()
