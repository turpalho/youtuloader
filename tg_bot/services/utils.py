import asyncio
import os
from datetime import datetime
import logging
import time

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import (Message,
                           FSInputFile,)
from aiogram.utils.markdown import hlink

from database.repository import DataFacade

# from tg_bot.filters.user import AddAdminFilter
from tg_bot.config import Config
from tg_bot.services.youtubeManager import (get_video_length,
                                            is_youtube_url,
                                            download_video_async,
                                            download_video,
                                            save_video_thumbnail)
from tg_bot.services.messages_text import messages_text
from tg_bot.keyboards.user import (get_subscribe_keyboard,)


def create_absolute_path(file_path: str, add_time: bool = False):
    full_file_path = f"{file_path}"
    if add_time:
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
        full_file_path += f"{formatted_datetime}"
    abs_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), full_file_path))

    return abs_file_path


async def get_video_thumvnail(video_url: str, thumbnail_path: str) -> FSInputFile:
    await save_video_thumbnail(video_url, thumbnail_path)
    thumb_file = FSInputFile(thumbnail_path)
    return thumb_file


async def downloader_youtube_video(message: Message,
                                   state: FSMContext,
                                   dataFacade: DataFacade,
                                   bot: Bot,
                                   config: Config) -> None:
    await state.clear()

    video_url = message.text
    if not is_youtube_url(video_url):
        await message.answer(text=messages_text["downloadError"])
        return

    video_name = f"video_{int(time.time())}.mp4"
    video_path = create_absolute_path(f"../../source/files/")
    full_path = f"{video_path}/{video_name}"

    try:
        video_length = await get_video_length(video_url, video_path, video_name)
        thumbnail_path = f"{full_path}_thumbnail.jpg"

        if video_length > 300:
            user = await dataFacade.get_user(user_id=message.chat.id)
            thumb_file = await get_video_thumvnail(video_url, full_path, thumbnail_path)
            if not user.premium:
                await message.answer(text=messages_text["unsubscribed"],
                                     reply_markup=await get_subscribe_keyboard())
                return
            else:
                downloading_message = await message.answer_photo(photo=thumb_file,
                                                                 caption=f'{messages_text["videoDownloading"]}\n   {video_url}')
                await download_video_async(video_url,
                                           video_path,
                                           video_name)
                await bot.send_message(chat_id=config.tg_bot.client_user_id,
                                       text=f"{message.chat.id}*_*{full_path}*_*{video_length}*_*{thumbnail_path}*_*{downloading_message.message_id}")
        else:
            thumb_file = await get_video_thumvnail(video_url, full_path, thumbnail_path)
            downloading_message = await message.answer_photo(photo=thumb_file,
                                                             caption=f'{messages_text["videoDownloading"]}\n   {video_url}')
            await download_video_async(video_url,
                                       video_path,
                                       video_name)

            video_file = FSInputFile(full_path)
            await message.answer_video(video=video_file,
                                       thumbnail=thumb_file,
                                       duration=video_length,
                                       caption=f'Скачивай видео с YouTube вместе с нами!\n\n{hlink("https://t.me/youtube_videoloader_bot", "https://t.me/youtube_videoloader_bot")}')
            await downloading_message.delete()

            try:
                await asyncio.sleep(2)
                os.remove(full_path)
                os.remove(thumbnail_path)
            except:
                logging.info("FileNotFoundError")
    except Exception as e:
        logging.info(e)
        await message.answer(text=messages_text["downloadError"])