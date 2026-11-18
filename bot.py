import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import database
from datetime import datetime, timedelta

TOKEN = "9102670058:AAFUfELnDIeGh5S3LI4w1a7B0J7YH3x-FUA"

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class AddHosting(StatesGroup):
    name = State()
    cost = State()
    date = State()
    interval = State()

logging.basicConfig(level=logging.INFO)

def main_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Список хостингов", callback_data="list_hostings")],
        [InlineKeyboardButton(text="Добавить хостинг", callback_data="add_hosting")],
        [InlineKeyboardButton(text="Статистика", callback_data="stats")],
        [InlineKeyboardButton(text="Админка", callback_data="admin_menu")]
    ])

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Главное меню:", reply_markup=main_menu_kb())

@dp.callback_query(F.data == "main_menu")
async def main_menu(callback: types.CallbackQuery, state: FSMContext = None):
    if state: await state.clear()
    try: await callback.answer()
    except: pass
    await callback.message.edit_text("Главное меню:", reply_markup=main_menu_kb())

@dp.callback_query(F.data == "add_hosting")
async def add_hosting_start(callback: types.CallbackQuery, state: FSMContext):
    try: await callback.answer()
    except: pass
    await state.set_state(AddHosting.name)
    await callback.message.edit_text("Введите название хостинга (или Назад):", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="main_menu")]]))

@dp.message(AddHosting.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddHosting.cost)
    await message.answer("Введите стоимость:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="add_hosting")]]))

@dp.message(AddHosting.cost)
async def process_cost(message: types.Message, state: FSMContext):
    await state.update_data(cost=float(message.text))
    await state.set_state(AddHosting.date)
    await message.answer("Введите дату начала (ГГГГ-ММ-ДД):", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="add_hosting_step2")]]))

@dp.message(AddHosting.date)
async def process_date(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text)
    await state.set_state(AddHosting.interval)
    await message.answer("Введите интервал оплаты в днях (напр. 30):", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="add_hosting_step3")]]))

@dp.message(AddHosting.interval)
async def process_interval(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await database.add_hosting(data['name'], data['cost'], data['date'], int(message.text))
    await message.answer("Хостинг добавлен!", reply_markup=main_menu_kb())
    await state.clear()

@dp.callback_query(F.data == "add_hosting_step2")
async def back_to_name(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AddHosting.cost)
    await callback.message.edit_text("Введите стоимость:")

@dp.callback_query(F.data == "list_hostings")
async def show_hostings(callback: types.CallbackQuery):
    try: await callback.answer()
    except: pass
    hostings = await database.get_hostings()
    builder = InlineKeyboardMarkup(inline_keyboard=[])
    for h in hostings:
        builder.inline_keyboard.append([InlineKeyboardButton(text=f"{h[1]}", callback_data=f"h_{h[0]}")])
    builder.inline_keyboard.append([InlineKeyboardButton(text="В главное меню", callback_data="main_menu")])
    
    if not hostings:
        await callback.message.edit_text("Список пуст.", reply_markup=builder)
    else:
        await callback.message.edit_text("Ваши хостинги:", reply_markup=builder)

@dp.callback_query(F.data.startswith("h_"))
async def host_actions(callback: types.CallbackQuery):
    h_id = callback.data.split("_")[1]
    builder = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Отметить оплату", callback_data=f"pay_{h_id}")],
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_{h_id}")],
        [InlineKeyboardButton(text="« Назад", callback_data="list_hostings")]
    ])
    await callback.message.edit_text("Выберите действие:", reply_markup=builder)
    await callback.answer()

@dp.callback_query(F.data.startswith("pay_"))
async def handle_payment(callback: types.CallbackQuery):
    h_id = callback.data.split("_")[1]
    await database.record_payment(h_id, 0, datetime.now().strftime('%Y-%m-%d'))
    await callback.message.edit_text("Оплата зафиксирована, дата обновлена!", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="В меню", callback_data="main_menu")]]))
    await callback.answer()

@dp.callback_query(F.data == "stats")
async def show_stats(callback: types.CallbackQuery):
    try: await callback.answer()
    except: pass
    hostings = await database.get_hostings()
    count = len(hostings)
    total_cost = sum([h[2] for h in hostings])
    await callback.message.edit_text(f"Статистика:\nВсего хостингов: {count}\nСумма в месяц: {total_cost}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="В главное меню", callback_data="main_menu")]]))

async def main():
    await database.init_db()
    # Уменьшаем нагрузку на сеть
    await dp.start_polling(bot, request_timeout=60, polling_timeout=60)

if __name__ == "__main__":
    asyncio.run(main())
