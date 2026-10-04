from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import engine, Base, get_session
from models import User, GarageItem, DrawnNumber
from game_logic import RARITY, gen_number, roll_rarity


ADMIN_IDS = [12345]
ADMIN_SECRET = "change_me_to_random_string_12345"


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_current_user_id(x_user_id: int = Header(...)) -> int:
    return x_user_id


async def get_or_create_user(session: AsyncSession, user_id: int) -> User:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(id=user_id, balance=100000, level=1, xp=0)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


@app.get("/")
def read_root():
    return {"message": "Сервер игры работает! 🚀"}


@app.get("/api/profile")
async def profile(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    user = await get_or_create_user(session, user_id)
    return {
        "id": user.id,
        "balance": float(user.balance),
        "level": user.level,
        "xp": user.xp,
        "xp_needed": user.level * 10,
    }


@app.post("/api/spin")
async def spin(
    country: str = "ru",
    guarantee: str = "any",
    cost: int = 1000,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    user = await get_or_create_user(session, user_id)

    if cost < 1000 or cost > 500000:
        raise HTTPException(status_code=400, detail="Неверная цена")

    if float(user.balance) < cost:
        raise HTTPException(status_code=400, detail="Недостаточно денег")

    user.balance = float(user.balance) - cost

    rarity = roll_rarity(guarantee)
    info = gen_number(rarity, country)

    for _ in range(10):
        exists = await session.execute(
            select(DrawnNumber).where(DrawnNumber.number == info['number'])
        )
        if exists.scalar_one_or_none() is None:
            break
        rarity = roll_rarity(guarantee)
        info = gen_number(rarity, country)

    session.add(DrawnNumber(number=info['number']))

    rarity_info = RARITY[rarity]
    final_price = info['final_price']

    earned = 0
    to_garage = False
    if rarity_info['to_garage']:
        item = GarageItem(
            user_id=user.id,
            number=info['number'],
            rarity=rarity,
            price=final_price,
        )
        session.add(item)
        to_garage = True
    else:
        earned = final_price
        user.balance = float(user.balance) + earned

    user.xp += rarity_info['xp']
    leveled_up = False
    while user.xp >= user.level * 10:
        user.xp -= user.level * 10
        user.level += 1
        leveled_up = True

    await session.commit()
    await session.refresh(user)

    return {
        "number": info['number'],
        "rarity": rarity,
        "rarity_name": rarity_info['name'],
        "series": info['series'],
        "digit_mult": info['digit_mult'],
        "series_mult": info['series_mult'],
        "region_mult": info['region_mult'],
        "total_mult": info['total_mult'],
        "base_price": info['base_price'],
        "final_price": info['final_price'],
        "to_garage": to_garage,
        "earned": earned,
        "balance": float(user.balance),
        "level": user.level,
        "xp": user.xp,
        "xp_needed": user.level * 10,
        "leveled_up": leveled_up,
    }


@app.get("/api/garage")
async def garage(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(GarageItem).where(
            GarageItem.user_id == user_id,
            GarageItem.sold == False,
        ).order_by(GarageItem.id.desc())
    )
    items = result.scalars().all()
    return [
        {"id": it.id, "number": it.number, "rarity": it.rarity, "price": it.price}
        for it in items
    ]


@app.post("/api/sell/{item_id}")
async def sell(
    item_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(GarageItem).where(
            GarageItem.id == item_id,
            GarageItem.user_id == user_id,
            GarageItem.sold == False,
        )
    )
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=404, detail="Номер не найден")

    user = await get_or_create_user(session, user_id)
    user.balance = float(user.balance) + item.price
    item.sold = True
    await session.commit()
    await session.refresh(user)
    return {"success": True, "earned": item.price, "balance": float(user.balance)}


@app.post("/api/admin/give")
async def admin_give(
    target_id: int,
    amount: int = 0,
    level: int = 0,
    xp: int = 0,
    x_admin_key: str = Header(...),
    session: AsyncSession = Depends(get_session),
):
    if x_admin_key != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Неверный админ-ключ")
    user = await get_or_create_user(session, target_id)
    if amount: user.balance = float(user.balance) + amount
    if level: user.level = level
    if xp: user.xp = xp
    await session.commit()
    await session.refresh(user)
    return {"success": True, "user_id": user.id, "balance": float(user.balance),
            "level": user.level, "xp": user.xp}


@app.post("/api/admin/reset")
async def admin_reset(
    target_id: int,
    x_admin_key: str = Header(...),
    session: AsyncSession = Depends(get_session),
):
    if x_admin_key != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Неверный админ-ключ")
    user = await get_or_create_user(session, target_id)
    user.balance = 100000
    user.level = 1
    user.xp = 0
    await session.commit()
    await session.refresh(user)
    return {"success": True, "user_id": user.id, "balance": float(user.balance), "level": user.level}


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/game")
async def game():
    return FileResponse("static/index.html")