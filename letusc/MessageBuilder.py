import json
from datetime import datetime

import requests

from letusc.logger import Log
from letusc.URLManager import URLManager
from letusc.util import env


class MessageBuilder:
    __logger = Log("MessageBuilder")

    def __init__(self, content: str = "", thread_id: str | None = None):
        self.username = env("BOT_DISCORD_USERNAME")
        self.avatar_url = URLManager.icon
        self.content = content
        self.webhook_url = f"{URLManager.discord_webhook}?wait=true"
        if thread_id:
            self.webhook_url = f"{self.webhook_url}&thread_id={thread_id}"

        self.author = {
            "name": env("BOT_DISCORD_AUTHOR_NAME"),
            "url": URLManager.github,
            "icon_url": URLManager.icon,
        }
        self.footer = {
            "text": "letusc - Letus Scraper",
            "icon_url": URLManager.icon,
        }
        self.thumbnail = {
            "url": URLManager.thumbnail,
        }

        self.embeds = []
        self.files = []

    def addEmbed(
        self,
        title: str,
        description: str,
        timestamp: datetime,
        url: str,
        color: int = 0xFF6600,
        fields: list[dict] = [],
    ):
        self.embeds.append(
            {
                "title": title,
                "description": description,
                "color": color,
                # "url": url,
                "timestamp": timestamp.isoformat(),
                "footer": self.footer,
                "thumbnail": self.thumbnail,
                "author": self.author,
                "fields": fields,
            }
        )
        if len(self.embeds) >= 10:
            self.send()
            self.embeds = []

    def build(self):
        return {
            "username": self.username,
            "content": self.content,
            "avatar_url": self.avatar_url,
            "embeds": self.embeds,
        }

    def send(self):
        __logger = Log(f"{self.__logger}.send")

        payload = self.build()
        res = requests.post(
            self.webhook_url,
            files=self.files,
            data={"payload_json": json.dumps(payload, ensure_ascii=False)},
        )

        __logger.debug(f"status_code: {res.status_code}")
