from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Sequence, String, func, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from database.db import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, index=True, type_=BigInteger)
    full_name: Mapped[Optional[str]]
    username: Mapped[Optional[str]]
    is_blocked: Mapped[bool]
    premium: Mapped[bool] = mapped_column(default=False)
    email: Mapped[Optional[str]]

    create_date = mapped_column(DateTime, server_default=func.now()) # index=True

    __mapper_args__ = {'eager_defaults': True}

    def __repr__(self) -> str:
        return f"User: #{self.user_id}"


class Payment(Base):
    __tablename__ = 'payments'

    id: Mapped[int] = mapped_column(Sequence('payments_id_seq'), primary_key=True, autoincrement=True, type_=BigInteger)
    user_id: Mapped[int] = mapped_column(type_=BigInteger)
    amount: Mapped[int] = mapped_column(type_=BigInteger)
    method: Mapped[str]

    create_date = mapped_column(DateTime, server_default=func.now()) # index=True

    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self) -> str:
        return f"Payment: #{self.id}"