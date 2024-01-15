import asyncio
import re
import sys
import time
from typing import List
from pytube import YouTube
import logging
import aiohttp

from tg_bot.services.tracebackManager import exception_hook

MAX_CONCURRENT_DOWNLOADS = 2
downloading_more_than_limit = False  # Флаг для отслеживания, что скачивается больше 5 видео
semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)


async def download_video_async(video_url: str, video_path: str, video_name: str, resolution: str) -> bool:
    # async with aiohttp.ClientSession() as session:
    global downloading_more_than_limit
    result = False
    async with semaphore:
        if semaphore._value == 0:
            downloading_more_than_limit = True
            logging.info("На данный момент скачивается больше 2 видео. Ожидайте...")
        try:
            yt = await asyncio.to_thread(YouTube, video_url)
            video = await asyncio.to_thread(yt.streams.filter(file_extension='mp4', res=resolution).first)
            await asyncio.to_thread(video.download, output_path=video_path, filename=video_name)
            result = True
        except Exception as e:
            logging.info(f"Ошибка при скачивании видео: {e}")
            exception_hook(*(sys.exc_info()))
        finally:
            if downloading_more_than_limit:
                # Если флаг установлен, сбрасываем его и выводим сообщение об окончании превышения лимита
                downloading_more_than_limit = False
                logging.info("Теперь можно продолжить скачивание видео.")
            return result

async def get_video_length(video_url: str) -> int:
    async with aiohttp.ClientSession() as session:
        yt = await asyncio.to_thread(YouTube, video_url)
        try:
            video_length = yt.length
            if video_length is not None:
                return video_length
            else:
                return 0
        except TypeError:
            return 0


async def get_video_resolution(video_url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        yt = await asyncio.to_thread(YouTube, video_url)
        try:
            all_streams = await asyncio.to_thread(yt.streams.filter(file_extension='mp4').order_by, 'resolution')
            if all_streams is not None:
                resolutions = {}
                for stream in all_streams:
                    resolutions[str(stream.resolution)] = (str(stream.resolution), f"{stream.filesize / (1024 * 1024):.2f}")
                return resolutions
            else:
                return {1:"Нет выбора"}
        except TypeError:
            return {1:"Нет выбора"}


async def get_thumbnail_url(video_url: str) -> None:
    async with aiohttp.ClientSession() as session:
        yt = await asyncio.to_thread(YouTube, video_url)
        return yt.thumbnail_url

        # async with session.get(thumbnail_url) as response:
        #     thumbnail_data = await response.read()

        # with open(thumbnail_path, 'wb') as thumbnail_file:
        #     thumbnail_file.write(thumbnail_data)


def is_youtube_url(url):
    # Регулярное выражение для проверки ссылки YouTube видео
    youtube_pattern = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

    # Пробуем найти соответствие
    match = re.match(youtube_pattern, url)

    return bool(match)