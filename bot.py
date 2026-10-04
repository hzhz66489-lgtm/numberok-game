import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram import F

BOT_TOKEN = os.getenv("8721077554:AAHFDoFTyn3LZARX05mW2MPveYdyvw_DJEo")
WEBAPP_URL = "https://numberok-game.onrender.com/game"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start_command(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎰 Играть",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ])
    await message.answer(
        "🚗 <b>Добро пожаловать в Номерок!</b>\n\n"
        "Крути номера, собирай редкие серии, зарабатывай миллионы.\n\n"
        "Нажми кнопку ниже, чтобы начать 👇",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "📖 <b>Помощь</b>\n\n"
        "🎰 /start — начать игру\n"
        "🎯 Крути номера, продавай красивые\n"
        "🏠 Редкие номера уходят в гараж\n"
        "🎡 Крути колесо фортуны раз в 2 часа",
        parse_mode="HTML"
    )


@dp.message(F.web_app_data)
async def web_app_data(message: types.Message):
    await message.answer(f"Получено: {message.web_app_data.data}")


async def start_bot():
    """Запускает бота (вызывается из main.py)."""
    if not BOT_TOKEN:
        print("⚠️ BOT_TOKEN не установлен — бот не запустится")
        return
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)