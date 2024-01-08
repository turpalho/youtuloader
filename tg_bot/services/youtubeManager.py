import asyncio
import re
import time
from pytube import YouTube
import logging
import aiohttp

async def download_video(video_url: str, video_path: str, video_name: str) -> None:
    yt = YouTube(video_url)
    video = yt.streams.get_highest_resolution()
    video.download(output_path=video_path, filename=video_name)


async def download_video_async(video_url: str, video_path: str, video_name: str) -> None:
    async with aiohttp.ClientSession() as session:
        yt = await asyncio.to_thread(YouTube, video_url)
        video = await asyncio.to_thread(yt.streams.get_highest_resolution)
        await asyncio.to_thread(video.download, output_path=video_path, filename=video_name)


async def get_video_length(video_url: str) -> int:
    async with aiohttp.ClientSession() as session:
        yt = await asyncio.to_thread(YouTube, video_url)
        video_length = yt.length

        return video_length


async def save_video_thumbnail(video_url: str, thumbnail_path: str) -> None:
    async with aiohttp.ClientSession() as session:
        yt = await asyncio.to_thread(YouTube, video_url)
        thumbnail_url = yt.thumbnail_url

        async with session.get(thumbnail_url) as response:
            thumbnail_data = await response.read()

        with open(thumbnail_path, 'wb') as thumbnail_file:
            thumbnail_file.write(thumbnail_data)


def is_youtube_url(url):
    # Регулярное выражение для проверки ссылки YouTube видео
    youtube_pattern = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

    # Пробуем найти соответствие
    match = re.match(youtube_pattern, url)

    return bool(match)