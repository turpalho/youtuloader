from aiogram.fsm.state import State, StatesGroup


class DownloadState(StatesGroup):
    waiting_send_video_url = State()