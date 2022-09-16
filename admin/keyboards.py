from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

# admin main buttons
load_btn = KeyboardButton('⬆️ Завантажити')
cancel_btn = KeyboardButton('⭕ Скасувати')
# fnd_btn = KeyboardButton('Знайти по id')
check_btn = KeyboardButton('📖Які товари закінчились?')
show_btn = KeyboardButton('🛒Всі товари')
exit_btn = KeyboardButton('🚪Вийти')
settings_btn = KeyboardButton('⚙️Налаштування')
orders_btn = KeyboardButton('🧾Замовлення')
# admin settings buttons

edit_start_img_btn = KeyboardButton('✏️Стартове фото')
edit_start_txt_btn = KeyboardButton('✏️Стартовий текст')
edit_location_btn = KeyboardButton('📍Змінити розташування')
edit_help_btn = KeyboardButton('❔Змінити хелп повідомлення')
edit_regime_btn = KeyboardButton('🕑Змінити режим')
back_btn = KeyboardButton('⬅️Назад')

# admin orders buttons
show_new = KeyboardButton('#📩Нові')
show_paid = KeyboardButton('#✅Оплачені')
show_canceled = KeyboardButton('#⛔Скасовані')
find_with_id = KeyboardButton('🔍ID')

# admin keyboards

# start(main) keyboard
admin_kb_start = ReplyKeyboardMarkup(resize_keyboard=True).add(load_btn). \
    row(check_btn, show_btn).row(settings_btn, orders_btn).add(exit_btn)
# cancel keyboard
admin_kb_cancel = ReplyKeyboardMarkup(resize_keyboard=True).add(cancel_btn)
# settings keyboard
admin_kb_settings = ReplyKeyboardMarkup(resize_keyboard=True) \
    .row(edit_start_txt_btn, edit_start_img_btn, edit_help_btn).row(edit_location_btn, edit_regime_btn).add(back_btn)
# order admin keyboard
admin_kb_orders = ReplyKeyboardMarkup(resize_keyboard=True).row(show_new, show_paid).row(show_canceled, find_with_id)\
    .add(back_btn)


# inline admin kb for product
def create_inline_admin_kb(prod_id: str):
    btn = InlineKeyboardButton(f'❌ Видалити', callback_data=f'Delete:{prod_id}')
    btn2 = InlineKeyboardButton(f'➕ Додати', callback_data=f'Add:{prod_id}')
    btn3 = InlineKeyboardButton(f'➖ Зменшити', callback_data=f'Div:{prod_id}')
    btn4 = InlineKeyboardButton(f'✏опис', callback_data=f'DescEdit:{prod_id}')
    btn5 = InlineKeyboardButton(f'✏️цінa', callback_data=f'PriceEdit:{prod_id}')
    btn6 = InlineKeyboardButton(f"✏️ім'я", callback_data=f'NameEdit:{prod_id}')
    btn7 = InlineKeyboardButton(f'✏️ фото', callback_data=f'ImgEdit:{prod_id}')
    kb = InlineKeyboardMarkup().row(btn, btn2, btn3).row(btn4, btn5, btn6).add(btn7)
    return kb


# inline admin kb for order
def create_order_inline_admin_kb(id: int):
    btn = InlineKeyboardButton('✅Оплачено', callback_data=f'Paid:{id}')
    btn2 = InlineKeyboardButton('🚫 Скасувати', callback_data=f'OrdCancel:{id}')
    btn3 = InlineKeyboardButton('❌ Видалити', callback_data=f'OrdDel:{id}')
    kb = InlineKeyboardMarkup().row(btn, btn2, btn3)
    return kb
