
# keyboards.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(
        KeyboardButton("📦 Тарифы"),
        KeyboardButton("📨 Поддержка")
    )
    kb.add(KeyboardButton("🧾 Мои заказы"))
    return kb

def tariff_list(dediks):
    kb = InlineKeyboardMarkup()
    for id_, name, price in dediks:
        kb.add(InlineKeyboardButton(f"{name} — ${price}", callback_data=f"buy:{id_}"))
    return kb

def duration_buttons(dedik_id):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("1 мес", callback_data=f"duration:{dedik_id}:1"),
        InlineKeyboardButton("3 мес", callback_data=f"duration:{dedik_id}:3"),
        InlineKeyboardButton("6 мес", callback_data=f"duration:{dedik_id}:6")
    )
    return kb
