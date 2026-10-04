from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, Integer, String, Numeric, Boolean
from database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram ID
    username: Mapped[str] = mapped_column(String(64), default="")
    balance: Mapped[float] = mapped_column(Numeric(12, 2), default=100000.00)
    level: Mapped[int] = mapped_column(Integer, default=1)
    xp: Mapped[int] = mapped_column(Integer, default=0)

class GarageItem(Base):
    __tablename__ = "garage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    number: Mapped[str] = mapped_column(String(16))       # А123ВС 77
    rarity: Mapped[str] = mapped_column(String(16))       # common / rare / ...
    price: Mapped[int] = mapped_column(Integer)
    sold: Mapped[bool] = mapped_column(Boolean, default=False)

class DrawnNumber(Base):
    """Все номера, которые когда-либо выпали — для уникальности"""
    __tablename__ = "drawn_numbers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    number: Mapped[str] = mapped_column(String(16), unique=True, index=True)