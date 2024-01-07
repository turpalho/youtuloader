from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message


class ComposerMiddleware(BaseMiddleware):
    def __init__(self, composer) -> None:
        self.composer = composer

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        data['composer'] = self.composer
        return await handler(event, data)
