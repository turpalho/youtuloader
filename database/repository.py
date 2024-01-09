import logging

from sqlalchemy import BigInteger, ScalarResult, exc, select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.ext.asyncio.engine import AsyncEngine

from tg_bot.models.users import User, Payment
from tg_bot.models.config import Config

logger = logging.getLogger(__name__)


class DataFacade:
    def __init__(self, engine: AsyncEngine):
        self.config_repo = ConfigRepo(engine)
        self.user_repo = UserRepo(engine)
        self.payment_repo = PaymentRepo(engine)

    async def get_config_parameters(self) -> Config:
        return await self.config_repo.get_config_parameters()

    async def create_config(self, admins_ids: list) -> None:
        return await self.config_repo.create_config(admins_ids)

    async def update_admin_ids(self, admins_ids: list) -> None:
        return await self.config_repo.update_admin_ids(admins_ids)

    async def get_users(self, is_blocked: bool = False) -> ScalarResult[User]:
        return await self.user_repo.get_users(is_blocked)

    async def get_user(self, user_id: int) -> User:
        return await self.user_repo.get_user(user_id)

    async def add_user(self, user_id: int, user_name: str | None, full_name: str | None) -> None:
        return await self.user_repo.add_user(user_id, user_name, full_name)

    async def update_user_premium(self, user_id: int, premium: bool, email: str) -> None:
        return await self.user_repo.update_user_premium(user_id, premium, email)

    async def add_payment(self, user_id: int, amount: int, method: str) -> None:
        return await self.payment_repo.add_payment(user_id, amount, method)


class ConfigRepo:
    def __init__(self, engine: AsyncEngine) -> None:
        self.async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async def get_config_parameters(self) -> Config:
        async with self.async_session_maker() as session:
            stmt = select(Config.__table__.columns).where(Config.id == 1)
            result = await session.execute(stmt)
        return result.first()

    async def create_config(self, admins_ids: list) -> None:
        async with self.async_session_maker() as session:
            new_str = str(admins_ids)[1:-1]
            session.add(Config(id=1, admins_ids=new_str))
            await session.commit()
        return

    async def update_admin_ids(self, admins_ids: list) -> None:
        async with self.async_session_maker() as session:
            new_str = str(admins_ids)[1:-1]
            stmt = update(Config).where(
                Config.id == 1).values(admins_ids=new_str)
            await session.execute(stmt)
            await session.commit()
        return


class UserRepo:
    def __init__(self, engine: AsyncEngine) -> None:
        self.async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async def get_users(self, is_blocked: bool | None = None) -> ScalarResult[User]:
        async with self.async_session_maker() as session:
            stmt = select(User.user_id)
            if is_blocked:
                stmt.where(User.is_blocked == is_blocked)
            stmt = stmt.order_by(User.user_id)
            result = await session.execute(stmt)
        return result.scalars()

    async def get_user(self, user_id: int) -> User:
        async with self.async_session_maker() as session:
            stmt = select(User).where(
                User.user_id == user_id)
            result = await session.execute(stmt)
        return result.scalar()

    async def get_user_time_sub(self, user_id: int) -> BigInteger | None:
        async with self.async_session_maker() as session:
            stmt = select(User.time_sub).where(
                User.user_id == user_id)
            result = await session.execute(stmt)
        return result.scalar()

    async def add_user(self, user_id: int, username: str | None, full_name: str | None,) -> None:
        async with self.async_session_maker() as session:
            try:
                user = User(user_id=user_id, is_blocked=False)

                if full_name:
                    user.full_name = full_name
                if username:
                    user.username = username

                session.add(user)
                await session.commit()
            except exc.IntegrityError:
                await session.rollback()
        return

    async def update_user_premium(self, user_id: int, premium: bool, email: str) -> None:
        async with self.async_session_maker() as session:
            stmt = update(User).where(User.user_id == user_id).values(premium=premium, email=email)
            await session.execute(stmt)
            await session.commit()
        return


class PaymentRepo:
    def __init__(self, engine: AsyncEngine) -> None:
        self.async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async def add_payment(self, user_id: int, amount: float, method: str):
        async with self.async_session_maker() as session:
            try:
                payment = Payment(
                    user_id=user_id,
                    amount=amount,
                    method=method
                )
                session.add(payment)
                await session.commit()
            except exc.IntegrityError:
                await session.rollback()
        return
