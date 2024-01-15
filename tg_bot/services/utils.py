import asyncio
import os
from datetime import datetime
import logging
import sys
import time

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import (Message,
                           CallbackQuery,
                           FSInputFile,
                           URLInputFile)
from aiogram.utils.markdown import hlink

from database.repository import DataFacade

# from tg_bot.filters.user import AddAdminFilter
from tg_bot.config import Config
from tg_bot.services.youtubeManager import (download_video_async)
from tg_bot.services.messages_text import messages_text
from tg_bot.keyboards.user import (get_back_keyboard)
from tg_bot.services.composer import Composer
from tg_bot.services.tracebackManager import exception_hook


def create_absolute_path(file_path: str, add_time: bool = False):
    full_file_path = f"{file_path}"
    if add_time:
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
        full_file_path += f"{formatted_datetime}"
    abs_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), full_file_path))

    return abs_file_path


def create_files_path():
    video_name = f"video_{int(time.time())}.mp4"
    video_path = create_absolute_path(f"../../source/files/")
    full_path = f"{video_path}/{video_name}"

    return (video_name, video_path, full_path)


async def downloader_youtube_video(call: CallbackQuery,
                                   state: FSMContext,
                                   video_url: str,
                                   bot: Bot,
                                   composer: Composer,
                                   video_name: str,
                                   video_path: str,
                                   full_path: str,
                                   thumb_url: str,
                                   resolution: str,
                                   duration: int) -> None:
    await state.clear()
    chat_id = call.message.chat.id

    try:
        thumb_file = URLInputFile(thumb_url)
        downloading_message = await call.message.answer_photo(photo=thumb_file, caption=f'{messages_text["videoDownloading"]}\n   {video_url}')
        result = await download_video_async(video_url, video_path, video_name, resolution)
        if result:
            try:
                video_file = FSInputFile(full_path)
                await call.message.answer_video(video=video_file, thumbnail=thumb_file, duration=duration, caption=messages_text['followus'])
            except:
                await composer.msg_handler.send_message(full_path, chat_id, duration, thumb_url, downloading_message.message_id)
        else:
            await call.message.answer(messages_text["downloadError"], reply_markup=await get_back_keyboard())

        await downloading_message.delete()

        try:
            await asyncio.sleep(2)
            os.remove(full_path)
        except:
            logging.info("FileNotFoundError")
    except Exception as e:
        exception_hook(*(sys.exc_info()))
        await call.message.answer(text=messages_text["downloadError"])

        try:
            os.remove(full_path)
        except:
            logging.info("FileNotFoundError")
