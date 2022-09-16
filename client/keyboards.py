from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# client buttons
regime_btn = KeyboardButton('🕑 Наш розклад')
location_btn = KeyboardButton('📍 Розташування')
catalog_btn = KeyboardButton('📜 Каталог')
orders_btn = KeyboardButton('🧾Мої замовлення')
cancel_btn = KeyboardButton('🚫 Скасувати')

# client keyboards
client_kb = ReplyKeyboardMarkup(resize_keyboard=True)
client_kb.row(regime_btn, location_btn).row(catalog_btn, orders_btn)
client_cancel_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(cancel_btn)


# client inline buttons for buy product
def create_inline_prod_btn(prod_id: str):
    btn = InlineKeyboardButton('💵 Замовити 💵', callback_data=f'Buy:{prod_id}')
    kb = InlineKeyboardMarkup().add(btn)
    return kb


# create inline buttons for cancel order
def create_inline_order_btn(ord_id: int):
    btn = InlineKeyboardButton('Скасувати', callback_data=f'CancOrd:{ord_id}')
    kb = InlineKeyboardMarkup().add(btn)
    return kb
