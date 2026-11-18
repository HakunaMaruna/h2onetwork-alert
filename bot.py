import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import database

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
ALERT_CHAT_ID = os.getenv("ALERT_CHAT_ID")

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

logging.basicConfig(level=logging.INFO)

@dp.message(Command("start"))
@dp.callback_query(F.data == "main_menu")
async def start_handler(event: types.Message | types.CallbackQuery, state: FSMContext = None):
    if state: await state.clear()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📂 Список хостингов", callback_data="list_hostings")],
        [InlineKeyboardButton(text="➕ Добавить хостинг", callback_data="add_hosting")]
    ])
    text = "Главное меню:"
    if isinstance(event, types.Message):
        await event.answer(text, reply_markup=kb)
    else:
        await event.message.edit_text(text, reply_markup=kb)
        await event.answer()

@dp.callback_query(F.data == "list_hostings")
async def list_hostings(callback: types.CallbackQuery):
    hostings = await database.get_hostings()
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for h in hostings:
        kb.inline_keyboard.append([InlineKeyboardButton(text=h[1], callback_data=f"h_{h[0]}")])
    kb.inline_keyboard.append([InlineKeyboardButton(text="« Назад", callback_data="main_menu")])
    await callback.message.edit_text("Ваши хостинги:", reply_markup=kb)
    await callback.answer()

async def main():
    await database.init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
