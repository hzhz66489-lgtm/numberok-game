from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# База данных — просто файл game.db в папке проекта
DATABASE_URL = "sqlite+aiosqlite:///./game.db"

# Движок — через него Python общается с БД
engine = create_async_engine(DATABASE_URL, echo=False)

# Сессия — «разговор» с базой
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Базовый класс для таблиц
class Base(DeclarativeBase):
    pass

# Функция для получения сессии (используем в эндпоинтах)
async def get_session():
    async with async_session() as session:
        yield session