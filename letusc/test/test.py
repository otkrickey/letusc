import json

from letusc.logger import L
from letusc.util import env


def test():
    # test_logger()
    test_model_v7()
    # exit(0)
    pass


def test_logger():
    from dataclasses import dataclass, field

    @dataclass
    class ClassA:
        _l = L()

        def __post_init__(self):
            self._l.i(self.__class__.__name__)
            self._l.info("A")

        def method_a(self):
            _l = self._l.gm(self.method_a.__name__)
            _l.info(f"method_a in {self.__class__.__name__}")

    @dataclass
    class ClassB(ClassA):
        _l = L()

        def __post_init__(self):
            self._l.i(self.__class__.__name__)
            self._l.info("B")

        def method_b(self):
            _l = self._l.gm(self.method_b.__name__)
            _l.info(f"method_b in {self.__class__.__name__}")

    class_a = ClassA()
    class_a.method_a()
    class_b = ClassB()
    class_b.method_a()
    class_b.method_b()
    class_a = ClassA()
    class_a.method_a()


def test_model_v7():
    _l = L("test_model_v7")
    # test_model_v7_letus(_l)
    # test_model_v7_discord(_l)
    # test_model_v7_page(_l)
    pass


def test_model_v7_letus(_l: L):
    _l = _l.gm("letus")

    from letusc.modelv7.letus import LetusUser

    letus_user = LetusUser(student_id=env("TUS_ID"))
    _l.debug("letus_user:")
    print(json.dumps(letus_user.to_api(), indent=4))

    from letusc.modelv7.letus import LetusUserWithPassword

    letus_user_with_password = LetusUserWithPassword(
        student_id=env("TUS_ID"),
        encrypted_password=env("VPN_PASS"),
    )
    _l.debug("letus_user_with_password:")
    print(str(json.dumps(letus_user_with_password.to_api(), indent=4)))

    from letusc.modelv7.cookie import Cookie
    from letusc.modelv7.letus import LetusUserWithCookies

    letus_user_with_cookies = LetusUserWithCookies(
        student_id=env("TUS_ID"),
        encrypted_password=env("VPN_PASS"),
        cookies=[
            Cookie(
                name="name",
                value="value",
                year="2023",
            )
        ],
    )
    _l.debug("letus_user_with_cookies:")
    print(str(json.dumps(letus_user_with_cookies.to_api(), indent=4)))


def test_model_v7_discord(_l: L):
    _l = _l.gm("discord")

    from letusc.modelv7.discord import DiscordUserAny

    discord_user_any = DiscordUserAny(discord_id=env("DISCORD_ID"))
    _l.debug("discord_user_any:")
    print(json.dumps(discord_user_any.to_api(), indent=4))

    from letusc.modelv7.discord import DiscordUser

    discord_user = DiscordUser(
        discord_id=env("DISCORD_ID"),
        username="otkrickey",
        discriminator="otkrickey",
    )
    _l.debug("discord_user:")
    print(json.dumps(discord_user.to_api(), indent=4))


def test_model_v7_page(_l: L):
    _l = _l.gm("page")

    # from letusc.modelv7.page import Page

    # page_base = Page.pull("2023:course:126936")
    # _l.debug("page_base:")
    # print(json.dumps(page_base.to_api(), indent=4))
    # from letusc.modelv7.page import NewPage

    # new_page = NewPage.create("2023:course:126936")
