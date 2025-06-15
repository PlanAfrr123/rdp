
# handlers.py
from aiogram import types
from aiogram.dispatcher import FSMContext
from config import dp, bot, ADMIN_ID, USDT_ADDRESS
from db import get_all_dediks, create_order, get_user_orders, mark_order_paid
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
import keyboards
from datetime import datetime

# --- FSM для email и срока ---
class Buy(StatesGroup):
    DEDIK_ID = State()
    DURATION = State()
    EMAIL = State()

# --- Команда /start ---
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    text = (
        "👋 <b>Добро пожаловать в магазин дедиков!</b>\n\n"
        "Выберите действие ниже:")
    await message.answer(text, parse_mode="HTML", reply_markup=keyboards.main_menu())

# --- Обработка кнопок главного меню ---
@dp.message_handler(lambda msg: msg.text == "📦 Тарифы")
async def show_tariffs(message: types.Message):
    dediks = get_all_dediks()
    await message.answer("📦 Доступные тарифы:", reply_markup=keyboards.tariff_list(dediks))

@dp.message_handler(lambda msg: msg.text == "📨 Поддержка")
async def support_msg(message: types.Message):
    await message.answer(
        "🛟 По всем вопросам обращайтесь:\n📧 <b>suppintelitainment@gmail.com</b>", parse_mode="HTML")

@dp.message_handler(lambda msg: msg.text == "🧾 Мои заказы")
async def my_orders(message: types.Message):
    orders = get_user_orders(message.from_user.id)
    if not orders:
        await message.answer("ℹ️ У вас пока нет заказов.")
        return
    text = "📄 Ваши заказы:\n"
    for name, duration, price, created in orders:
        text += f"• {name} — {duration} мес — {price}$ — {created[:10]}\n"
    await message.answer(text)

# --- После выбора тарифа ---
@dp.callback_query_handler(lambda c: c.data and c.data.startswith("buy:"))
async def choose_duration(callback: types.CallbackQuery, state: FSMContext):
    dedik_id = int(callback.data.split(":")[1])
    await state.update_data(dedik_id=dedik_id)
    await Buy.DURATION.set()

    await callback.message.answer(
        "⏳ Выберите срок аренды:",
        reply_markup=keyboards.duration_buttons(dedik_id))
    await callback.answer()

# --- После выбора срока ---
@dp.callback_query_handler(lambda c: c.data and c.data.startswith("duration:"), state=Buy.DURATION)
async def ask_email(callback: types.CallbackQuery, state: FSMContext):
    _, dedik_id, months = callback.data.split(":")
    await state.update_data(dedik_id=int(dedik_id), duration=int(months))
    await Buy.EMAIL.set()
    await callback.message.answer("✉️ Введите ваш email для связи:")
    await callback.answer()

# --- После ввода email ---
@dp.message_handler(state=Buy.EMAIL)
async def handle_email(message: types.Message, state: FSMContext):
    data = await state.get_data()
    dedik_id = data["dedik_id"]
    duration = data["duration"]
    email = message.text.strip()

    # Получение тарифа и цены
    dediks = get_all_dediks()
    name, base_price = next((n, p) for (i, n, p) in dediks if i == dedik_id)

    if base_price == 5:
        price = {1: 5, 3: 25, 6: 50}[duration]
    elif base_price == 19.99:
        price = {1: 19.99, 3: 55, 6: 100}[duration]
    elif base_price == 59.99:
        price = {1: 59.99, 3: 165, 6: 300}[duration]
    else:
        price = base_price * duration

    order_id = create_order(message.from_user.id, email, dedik_id, duration, price)

    # Кнопка "Оплатил"
    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton("✅ Я оплатил", callback_data=f"paid:{order_id}")
    )

    text = (
        f"<b>Ваш заказ #{order_id}</b>\n"
        f"Тариф: <b>{name}</b> — {duration} мес — ${price}\n"
        f"💳 Оплата USDT (TRC20) на адрес:\n<code>{USDT_ADDRESS}</code>\n\n"
        f"После оплаты нажмите кнопку ниже."
    )
    await message.answer(text, parse_mode="HTML", reply_markup=kb)

    await bot.send_message(
        ADMIN_ID,
        f"🆕 Новый заказ #{order_id}\nEmail: {email}\nТариф: {name} — {duration} мес — ${price}"
    )

    await state.finish()

# --- Обработка кнопки "Оплатил" ---
@dp.callback_query_handler(lambda c: c.data and c.data.startswith("paid:"))
async def process_paid(callback: types.CallbackQuery):
    order_id = int(callback.data.split(":")[1])

    mark_order_paid(order_id)

    await callback.message.edit_reply_markup()
    await bot.send_message(callback.from_user.id, "✅ Спасибо! Ожидайте — доступ будет отправлен на вашу почту.")
    await bot.send_message(ADMIN_ID, f"✅ Заказ #{order_id} отмечен как оплаченный.")
    await callback.answer()
