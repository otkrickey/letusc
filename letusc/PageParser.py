from dataclasses import dataclass

from letusc.logger import L
from letusc.modelv7.account import Account
from letusc.modelv7.code import PageCode
from letusc.modelv7.content import Content
from letusc.modelv7.module import Module
from letusc.modelv7.page import NewPage, Page
from letusc.task.discord_task import DiscordChatThread, EmbedBuilder

__all__ = [
    "Parser",
]


@dataclass
class Parser:
    _l = L()
    page: NewPage
    _page: Page | None = None

    @classmethod
    async def create(cls, multi_id: str, code: PageCode) -> "Parser":
        cls._l = L(cls.__name__)
        _l = cls._l.gm("get")
        _account = await Account.pull(multi_id)
        cookie = _account.get_cookie(code.year)
        # page, _page = await asyncio.gather(
        #     NewPage.parse(_code, cookie),
        #     Page.pull(_code.code),
        #     return_exceptions=True,
        # )
        # if not isinstance(page, NewPage):
        #     raise page
        # if not isinstance(_page, Page):
        #     if L("Page").gm("pull").c("NotFound") in str(_page):
        #         raise _page
        #     else:
        #         raise _page
        # return cls(page=page, _page=_page)
        page = await NewPage.parse(code, cookie)
        return cls(page=page)

    @classmethod
    async def from_page(cls, _page: Page) -> "Parser":
        _l = L(cls.__name__).gm("from_page")
        _code = PageCode.create(_page.code)
        account = await Account.pull(_page.accounts[0])
        cookie = account.get_cookie(_code.year)
        page = await NewPage.parse(_code, cookie)
        return cls(page=page, _page=_page)

    async def compare(self) -> bool:
        _l = self._l.gm("compare")
        if not self._page:
            _l.debug("The page does not exist in the database.")
            await self._compare(False)
            # await self.page.push()
            return True
        if self.page.hash == self._page.hash:
            _l.debug("The page has not changed.")
            return False
        _l.debug("The page has changed.")
        await self._compare(True)
        # await self.page.push()
        return True

    async def _compare(self, notify=True, push=True) -> None:
        _l = self._l.gm("_compare")
        contents = self.page.contents
        _contents = self._page.contents if self._page else {}

        chats = (
            [
                await DiscordChatThread.get(channel_id=int(k), thread_id=int(v))
                for k, v in self._page.chat.items()
            ]
            if self._page
            else []
        )

        for content_key, content in contents.items():
            if content_key in _contents.keys():
                if content.hash != _contents[content_key].hash:
                    builder = EmbedBuilder.from_model(self.page, content, "changed")
                    _content = await Content.pull(content_key)

                    for module_key, module in content.modules.items():
                        if module_key in _content.modules.keys():
                            if module.hash != _content.modules[module_key].hash:
                                builder.add_field_from_model(module, "changed")
                                await module.push()

                        else:
                            builder.add_field_from_model(module, "new")
                            await module.push()

                    for module_key in _content.modules.keys():
                        if module_key not in content.modules.keys():
                            builder.add_field_from_model(
                                module=await Module.pull(module_key),
                                status="deleted",
                            )

                    if notify:
                        for chat in chats:
                            await chat.SendFromBuilder(builder)
                    await content.push()

            else:
                builder = EmbedBuilder.from_model(self.page, content, "new")

                for module_key, module in content.modules.items():
                    builder.add_field_from_model(module, "new")
                    await module.push()

                if notify:
                    for chat in chats:
                        await chat.SendFromBuilder(builder)
                await content.push()

        for content_key in _contents.keys():
            if content_key not in contents.keys():
                _content = await Content.pull(content_key)
                builder = EmbedBuilder.from_model(self.page, _content, "deleted")
                for module_key in _content.modules.keys():
                    builder.add_field_from_model(
                        module=await Module.pull(module_key),
                        status="deleted",
                    )

                if notify:
                    for chat in chats:
                        await chat.SendFromBuilder(builder)

        _l.info("The page has been updated.")
