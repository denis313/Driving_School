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
    total: Mapped[int] = mapped_column(default=0)
    status = mapped_column(Boolean, default=False)
    doc: Mapped[str] = mapped_column(nullable=True)
    request = mapped_column(Boolean)
    reg = mapped_column(Boolean, default=False)
    adult = mapped_column(Boolean)
    buy = mapped_column(Boolean, default=False)
    email: Mapped[str] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(nullable=True)
    phone: Mapped[str] = mapped_column(nullable=True)
    end_date = mapped_column(Date)

    def __repr__(self) -> str:
        ...
        return f"Users: id: {self.id_user}, user_id: {self.user_id}, status: {self.status}"


class Links(Base):
    __tablename__ = 'links'

    id_link: Mapped[int] = mapped_column(primary_key=True)
    status = mapped_column(Boolean)
    link: Mapped[str] = mapped_column()

    def __repr__(self) -> str:
        ...
        return f"LiNKS: id: {self.id_link},status: {self.status}, link: {self.link}"
