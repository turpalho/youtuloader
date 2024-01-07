from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from tg_bot.config import Config


class CallbackDataFilter(BaseFilter):

    def __init__(self, data) -> None:
        self.data = data

    async def __call__(self, obj: CallbackQuery) -> bool:
        return obj.data == self.data


class AddAdminFilter(BaseFilter):

    async def __call__(self, obj: Message, config: Config) -> bool:
        return obj.text == config.misc.add_admin_cmd
