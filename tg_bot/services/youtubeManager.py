import asyncio
import re
import time
from pytube import YouTube
import logging
import aiohttp

def download_video(video_url: str, video_path: str, video_name: str) -> None:
    yt = YouTube(video_url)

    # Выберите качество видео (может потребоваться некоторое время для поиска)
    video = yt.streams.get_highest_resolution()

    # Укажите путь, куда сохранить видео
    video.download(output_path=video_path, filename=video_name)


async def download_video_async(video_url: str, video_path: str, video_name: str) -> None:
    async with aiohttp.ClientSession() as session:
        yt = await asyncio.to_thread(YouTube, video_url)
        video = await asyncio.to_thread(yt.streams.get_highest_resolution)
        await asyncio.to_thread(video.download, output_path=video_path, filename=video_name)


async def get_video_length(video_url: str, video_path: str, video_name: str) -> int:
    async with aiohttp.ClientSession() as session:
        yt = await asyncio.to_thread(YouTube, video_url)

        # Получаем URL обложки
        thumbnail_url = yt.thumbnail_url

        # Асинхронно загружаем обложку
        async with session.get(thumbnail_url) as response:
            thumbnail_data = await response.read()

         # Сохраняем обложку
        thumbnail_path = f"{video_path}/{video_name}_thumbnail.jpg"
        with open(thumbnail_path, 'wb') as thumbnail_file:
            thumbnail_file.write(thumbnail_data)


        # Получить длительность видео в секундах
        video_length = yt.length

        return video_length


def is_youtube_url(url):
    # Регулярное выражение для проверки ссылки YouTube видео
    youtube_pattern = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

    # Пробуем найти соответствие
    match = re.match(youtube_pattern, url)

    return bool(match)