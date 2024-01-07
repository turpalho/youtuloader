from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import DeclarativeBase

# from tg_bot.config import settings


convention = {
    'all_column_names': lambda constraint, table: '_'.join([
        column.name for column in constraint.columns.values()
    ]),
    'ix': 'ix__%(table_name)s__%(all_column_names)s',
    'uq': 'uq__%(table_name)s__%(all_column_names)s',
    'ck': 'ck__%(table_name)s__%(constraint_name)s',
    'fk': (
        'fk__%(table_name)s__%(all_column_names)s__'
        '%(referred_table_name)s'
    ),
    'pk': 'pk__%(table_name)s'
}

metadata = MetaData(naming_convention=convention)


# Registry for all tables
class Base(DeclarativeBase):
    metadata = metadata


async def create_db(db_url: str, echo: bool) -> AsyncEngine:
    engine = create_async_engine(
        url=db_url,
        echo=echo
    )
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    return engine


async def dispose_db(engine: AsyncEngine) -> None:
    await engine.dispose()
