from typing import List, Optional

from sqlalchemy import BigInteger, Boolean, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = 'users'

    id_user: Mapped[int] = mapped_column(primary_key=True)
    user_id = mapped_column(BigInteger, nullable=True, unique=True)
    telegram_id = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str] = mapped_column()
    subscription_status = mapped_column(Boolean)
    subscription_start_date = mapped_column(Date)
    subscription_end_date = mapped_column(Date)

    def __repr__(self) -> str:
        ...
        return (f"Users: id: {self.id_user}, user_id: {self.user_id}, telegram_id: {self.telegram_id}, "
                f"username: {self.username}, subscription_status: {self.subscription_status}, "
                f"subscription_start_date: {self.subscription_start_date}")

