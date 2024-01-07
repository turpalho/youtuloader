from dataclasses import dataclass

from environs import Env


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str


@dataclass
class TgBot:
    token: str
    bot_name: str
    admin_ids: list[int]
    yookassa_token: str
    use_redis: bool
    bot_username: str
    client_phone_number: str
    client_session_name: str
    client_api_id: str
    client_api_hash: str
    client_chat_username: str
    client_user_id: int


@dataclass
class Miscellaneous:
    add_admin_cmd: str | None = None
    other_params = None


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    misc: Miscellaneous

    @property
    def DATABASE_URL(self):
        return (f'postgresql+asyncpg://{self.db.user}:{self.db.password}@{self.db.host}/{self.db.database}')


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str('BOT_TOKEN'),
            bot_name=env.str('BOT_NAME'),
            admin_ids=list(map(int, env.list('ADMINS'))),
            yookassa_token=env.str('YOOKASSA_TOKEN'),
            use_redis=env.bool('USE_REDIS'),
            bot_username=env.str('BOT_USER_NAME'),
            client_phone_number=env.str('TELEGRAM_PHONE'),
            client_session_name=env.str('SESSION_NAME'),
            client_api_id=env.str('API_ID'),
            client_api_hash=env.str('API_HASH'),
            client_chat_username=env.str('CLIENT_CHAT_USERNAME'),
            client_user_id=env.int('CLIENT_USER_ID'),
        ),
        db=DbConfig(
            host=env.str('DB_HOST'),
            password=env.str('DB_PASS'),
            user=env.str('DB_USER'),
            database=env.str('DB_NAME')
        ),
        misc=Miscellaneous(
            add_admin_cmd=env.str('ADD_ADMIN_CMD')
        )
    )
