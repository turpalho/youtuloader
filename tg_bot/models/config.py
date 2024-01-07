from sqlalchemy.orm import Mapped, mapped_column

from database.db import Base


class Config(Base):
    __tablename__ = 'config'

    id: Mapped[int] = mapped_column(primary_key=True)
    admins_ids: Mapped[str]

    __mapper_args__ = {'eager_defaults': True}

    def __repr__(self) -> str:
        return f"Config: #{self.admins_ids}"