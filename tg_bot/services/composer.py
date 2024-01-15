import logging
import os
import re

from telethon import TelegramClient, events
from telethon.tl.types import DocumentAttributeVideo, InputMediaUploadedDocument, InputFile

from tg_bot.config import Config

logger = logging.getLogger(__name__)


class Composer:
    """Composition of telegram client interfaces"""

    def __init__(self, client: TelegramClient, config: Config):
        self._client = client
        self.msg_handler = MessageHandler(client, config)


class MessageHandler:
    def __init__(self, client: TelegramClient, config: Config):
        self._client = client
        self.config = config

    async def send_message(self, video_path: str, user_id: int, duration: int, thumb_url: str, downloading_message: int):

        video_attributes = [
            DocumentAttributeVideo(
                duration=duration,
                w=1280,
                h=720,
            ),
        ]

        await self._client.send_file(
            entity=self.config.tg_bot.bot_user_id,
            file=video_path,
            mime_type='video/mp4',
            attributes=video_attributes,
            caption=f"{user_id}*_*{downloading_message}*_*{thumb_url}"
            )

        try:
            os.remove(video_path)
        except:
            print("FileNotFoundError")
