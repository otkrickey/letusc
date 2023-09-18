import json
from dataclasses import dataclass
from datetime import datetime
from os import path
from typing import Literal

import discord
from discord import Embed, EmbedField, TextChannel, Thread, User
from discord.abc import Messageable
from discord.ui import View

from letusc.logger import L
from letusc.modelv7.content import ContentBase
from letusc.modelv7.module import ModuleBase
from letusc.modelv7.page import PageBase
from letusc.URLManager import URLManager

from ..bot import LetusBotClient

__all__ = [
    "status_",
    "EmbedBuilder",
    "DiscordChat",
    "DiscordChatUser",
    "DiscordChatChannel",
    "DiscordChatThread",
]


status_ = Literal["new", "changed", "deleted"]
with open(
    path.abspath(path.join(path.dirname(__file__), "./embed_settings.json")),
    "r",
) as f:
    settings = json.load(f)


class EmbedBuilder(Embed):
    _l = L()

    def __init__(self, *args, **kwargs):
        self._content: str | None = kwargs.pop("_content", None)
        super().__init__(*args, **kwargs)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__init__")
        self.set_footer(
            text="letusc - Letus Scraper",
            icon_url=URLManager.icon,
        )
        self.set_thumbnail(url=URLManager.thumbnail)
        # self.set_image(url=URLManager.image)
        self.set_author(
            name="letusc",
            url=URLManager.github,
            icon_url=URLManager.icon,
        )

    @staticmethod
    def _get_color(status: status_) -> int:
        _l = L(EmbedBuilder.__name__).gm("_get_color")
        match status:
            case "new":
                return 0x3FB950
            case "changed":
                return 0xD29922
            case "deleted":
                return 0xF85149

    @staticmethod
    def _get_status(status: status_) -> str:
        _l = L(EmbedBuilder.__name__).gm("_get_status")
        match status:
            case "new":
                return "追加"
            case "changed":
                return "更新"
            case "deleted":
                return "削除"

    @classmethod
    def from_model(
        cls, page: PageBase, content: ContentBase, status: status_
    ) -> "EmbedBuilder":
        _l = L(cls.__name__).gm("from_model")
        return cls(
            _content=f"{page.title}「{content.title}」({page.code})が{cls._get_status(status)}されました！",
            title=content.title,
            description=content.main,
            url=content.url,
            timestamp=content.timestamp,
            color=cls._get_color(status),
        )

    @classmethod
    def from_json(cls, key: str, **kwargs) -> "EmbedBuilder":
        _l = L(cls.__name__).gm("from_json")
        try:
            setting = settings.get(key)
            setting_str = json.dumps(setting)
            for key, value in kwargs.items():
                setting_str = setting_str.replace(f"{{{key}}}", str(value))
            setting = json.loads(setting_str)
            return cls(
                _content=setting.get("content"),
                title=setting.get("title"),
                description=setting.get("description"),
                url=setting.get("url"),
                timestamp=datetime.now(),
                color=setting.get("color"),
                fields=[
                    EmbedField(
                        name=field.get("name"),
                        value=field.get("value"),
                        inline=field.get("inline"),
                    )
                    for field in setting.get("fields")
                ],
            )
        except Exception as e:
            raise ValueError(_l.c("InvalidArgument")) from e

    def add_field_from_model(self, module: ModuleBase, status: status_):
        _l = self._l.gm("add_field_from_model")
        code = f"`{module.module_type}:{module.module_id}`"
        self.add_field(
            name=f"[{module.module_type}] {module.title} ({status}!)",
            value=f"{module.main or 'no description'}\n[{code}]({module.module_url or module.url})",
            inline=False,
        )


@dataclass
class DiscordChat:
    _l = L()
    chat: Messageable
    user_id: int | None = None
    channel_id: int | None = None
    thread_id: int | None = None

    def __post_init__(self):
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")

    @classmethod
    async def get(
        cls,
        user_id: int | None = None,
        channel_id: int | None = None,
        thread_id: int | None = None,
    ) -> "DiscordChat":
        _l = L(cls.__name__).gm("get")
        if user_id:
            return await DiscordChatUser.get(user_id)
        if channel_id and not thread_id:
            return await DiscordChatChannel.get(channel_id)
        if channel_id and thread_id:
            return await DiscordChatThread.get(channel_id, thread_id)
        raise ValueError(_l.c("InvalidArgument"))

    async def SendMessage(self, content: str):
        _l = self._l.gm("SendMessage")
        await self.chat.send(content)

    async def SendEmbedMessage(self, content: str | None, embed: Embed):
        _l = self._l.gm("SendEmbedMessage")
        await self.chat.send(content, embed=embed)

    async def SendFromBuilder(self, builder: EmbedBuilder, view: View | None = None):
        _l = self._l.gm("SendFromBuilder")
        if view:
            await self.chat.send(content=builder._content, embed=builder, view=view)
        else:
            await self.chat.send(content=builder._content, embed=builder)

    @classmethod
    async def getByID(cls, id: int) -> "DiscordChat":
        _l = L(cls.__name__).gm("getByID")
        client = await LetusBotClient.get_client()
        chat = client.get_channel(id)
        if not chat:
            chat = client.get_user(id)
        if isinstance(chat, User):
            return DiscordChatUser(chat)
        if isinstance(chat, TextChannel):
            return DiscordChatChannel(chat)
        if isinstance(chat, Thread):
            return DiscordChatThread(chat)
        raise ValueError(_l.c("ChatNotFound"))

    @classmethod
    async def getByCTX(cls, ctx) -> "DiscordChat":
        _l = L(cls.__name__).gm("getByCTX")
        _ = await cls.getByID(ctx.interaction.channel_id)
        setattr(_, "ctx", ctx)
        return _

    def getCTX(self) -> discord.ApplicationContext | None:
        _l = self._l.gm("getCTX")
        return getattr(self, "ctx", None)


@dataclass
class DiscordChatUser(DiscordChat):
    _l = L()
    chat: User
    user_id: int
    channel_id = None
    thread_id = None

    def __post_init__(self):
        DiscordChat.__post_init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")

    @classmethod
    async def get(cls, user_id: int) -> "DiscordChatUser":
        _l = L(cls.__name__).gm("get")
        client = await LetusBotClient.get_client()
        user = client.get_user(user_id)
        if not isinstance(user, User):
            raise ValueError(_l.c("UserNotFound"))
        return cls(chat=user, user_id=user_id)


@dataclass
class DiscordChatChannel(DiscordChat):
    _l = L()
    chat: TextChannel
    user_id = None
    channel_id: int
    thread_id = None

    def __post_init__(self):
        DiscordChat.__post_init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")

    @classmethod
    async def get(cls, channel_id: int) -> "DiscordChatChannel":
        _l = L(cls.__name__).gm("get")
        client = await LetusBotClient.get_client()
        channel = client.get_channel(channel_id)
        if not isinstance(channel, TextChannel):
            raise ValueError(_l.c("ChannelNotFound"))
        return cls(chat=channel, channel_id=channel_id)


@dataclass
class DiscordChatThread(DiscordChat):
    _l = L()
    chat: Thread
    user_id = None
    channel_id: int
    thread_id: int

    def __post_init__(self):
        DiscordChat.__post_init__(self)
        self._l = L(self.__class__.__name__)
        _l = self._l.gm("__post_init__")

    @classmethod
    async def get(cls, channel_id: int, thread_id: int) -> "DiscordChatThread":
        _l = L(cls.__name__).gm("get")
        client = await LetusBotClient.get_client()
        channel = client.get_channel(channel_id)
        if not isinstance(channel, TextChannel):
            raise ValueError(_l.c("ChannelNotFound"))
        thread = channel.get_thread(thread_id)
        if not isinstance(thread, Thread):
            raise ValueError(_l.c("ThreadNotFound"))
        return cls(chat=thread, channel_id=channel_id, thread_id=thread_id)
