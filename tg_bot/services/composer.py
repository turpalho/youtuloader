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
        self._msg_handler = MessageHandler(client, config)
        self._client.on(events.NewMessage(chats=self._msg_handler.chats))(self._msg_handler.handle)


class MessageHandler:
    def __init__(self, client: TelegramClient, config: Config):
        self._client = client
        self.config = config
        self.chats = [self.config.tg_bot.bot_username, "nart_erstho"]

    async def handle(self, event):
        try:
            message = event.message.message
            data = message.split("*_*")
            user_id = data[0]
            video_path = data[1]
            video_duration = int(data[2])
            thumbnail_path = data[3]
            downloading_message = data[4]
            await self._send_message(video_path, user_id, video_duration, thumbnail_path, downloading_message)
        except:
            logging.info("Не удалось отправить сообщение!")

    async def _send_message(self, video_path: str, user_id: str, duration: int, thumbnail_path: str, downloading_message: str):

        video_attributes = [
            DocumentAttributeVideo(
                duration=duration,  # укажите длительность видео в секундах
                w=1280,  # ширина видео
                h=720,  # высота видео
            ),
        ]

        video_message = await self._client.send_file(
            entity=-1001583881155,
            file=video_path,
            mime_type='video/mp4',
            attributes=video_attributes,
            thumb=thumbnail_path,
            )


        video_message_url = f"https://t.me/{self.config.tg_bot.client_chat_username}/{video_message.id}"
        await self._client.send_message(entity=self.config.tg_bot.bot_username,
                                        message=f"{user_id}*_*{video_message_url}*_*{video_message.id}*_*{downloading_message}")

        try:
            os.remove(video_path)
            os.remove(thumbnail_path)
        except:
            print("FileNotFoundError")
