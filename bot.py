import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage

from sqlalchemy.ext.asyncio.engine import AsyncEngine
from telethon import TelegramClient

from database.db import create_db, dispose_db
from database.repository import DataFacade
from tg_bot.config import Config, load_config
from tg_bot.handlers.user import user_router
from tg_bot.middlewares.config import ConfigMiddleware
from tg_bot.middlewares.db_middleware import DbMiddleware
from tg_bot.middlewares.composer_middleware import ComposerMiddleware
from tg_bot.services.composer import Composer

logger = logging.getLogger(__name__)

bot_commands = [
    types.BotCommand(command="/start", description="Главное меню"),
    types.BotCommand(command="/help", description="Инструкция"),
    types.BotCommand(command="/premium", description="Premium"),
]


async def on_shutdown(pool) -> None:
    await dispose_db(pool)


async def create_pool(db_url, echo) -> AsyncEngine:
    engine = await create_db(db_url, echo)
    return engine


async def restore_config(config: Config, dataFacade: DataFacade) -> None:
    config_parameters = await dataFacade.get_config_parameters()
    if config_parameters:
        admin_ids = [int(admin_id) for admin_id in config_parameters.admins_ids.split(",")]
        config.tg_bot.admin_ids = admin_ids
        # config.misc.contest_ended = config_parameters[0].contest_ended
    else:
        await dataFacade.create_config(config.tg_bot.admin_ids)


def register_global_middlewares(dp: Dispatcher,
                                config: Config,
                                pool: AsyncEngine,
                                dataFacade: DataFacade,
                                composer: Composer) -> None:
    dp.message.outer_middleware(ConfigMiddleware(config))
    dp.callback_query.outer_middleware(ConfigMiddleware(config))

    dp.message.outer_middleware(ComposerMiddleware(composer))
    dp.callback_query.outer_middleware(ComposerMiddleware(composer))

    dp.message.middleware(DbMiddleware(pool, dataFacade))
    dp.callback_query.outer_middleware(DbMiddleware(pool, dataFacade))


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config(".env")

    storage = MemoryStorage()

    pool = await create_pool(
        db_url=config.DATABASE_URL,
        echo=False,
    )
    dataFacade = DataFacade(pool)

    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(storage=storage)

    client = TelegramClient(config.tg_bot.client_session_name,
                            config.tg_bot.client_api_id,
                            config.tg_bot.client_api_hash)
    await client.start(phone=config.tg_bot.client_phone_number)
    composer = Composer(client=client, config=config)

    await bot.set_my_commands(bot_commands)

    # routers and middlewares registration
    for router in [
        # admin_router,
        user_router
    ]:
        dp.include_router(router)

    await restore_config(config, dataFacade)


    register_global_middlewares(dp, config, pool, dataFacade, composer)

    # start bot
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    await composer.client.run_until_disconnected()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Бот отключен")
