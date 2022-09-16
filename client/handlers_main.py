from aiogram.dispatcher import FSMContext
from create_bot import bot
from aiogram import types, Dispatcher
from database import sqlite_bot
from aiogram.dispatcher.filters import Text
from . import keyboards, handlers_order


# handler for start and help command
async def start_command_handler(message: types.Message):
    if message.text == '/start':
        try:
            await bot.send_photo(message.from_user.id, sqlite_bot.get_param_from_bt('start_img'),
                                 sqlite_bot.get_param_from_bt('start_text'),
                                 reply_markup=keyboards.client_kb)
            await message.delete()
        except Exception:
            await message.reply('Спілкування з ботом через ПП')
    if message.text == '/help':
        await bot.send_message(message.from_user.id, sqlite_bot.get_param_from_bt('help'))
        await message.delete()


# handler for location button
async def location_button_handler(message: types.Message):
    await bot.send_message(message.from_user.id, sqlite_bot.get_param_from_bt('location'))
    await message.delete()


# handler for regime button
async def regime_button_handler(message: types.Message):
    await bot.send_message(message.from_user.id, sqlite_bot.get_param_from_bt('regime'))
    await message.delete()


# handler for catalog button
async def catalog_button_handler(message: types.Message):
    for product in sqlite_bot.select_catalog():
        await bot.send_photo(message.from_user.id, product[0], f'id: {product[1]}\nНазва товару: {product[2]}\n'
                                                               f'Опис:\n{product[3]}\nЦіна: {product[4]} UAH',
                             reply_markup=keyboards.create_inline_prod_btn(prod_id=product[1]))
    await message.delete()


# showing all user orders
async def user_orders_button_handler(message: types.Message):
    for order in sqlite_bot.find_order_by_user(message.from_user.id):
        await bot.send_message(message.from_user.id, f'id замовлення: {order[0]}\n'
                                                     f'id товару: {order[2]}\n'
                                                     f'к-ть: {order[3]} pcs\n'
                                                     f'всього: {order[4]} UAH\n'
                                                     f'буде доставлено: {order[5]}\n'
                                                     f'дата замовлення: {order[6]}\nстатус: {order[7]}',
                               reply_markup=keyboards.create_inline_order_btn(order[0]))
        await message.delete()


# handler for cancel any state
async def cancel_button_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await state.reset_data()
    await message.reply('Cкасовано', reply_markup=keyboards.client_kb)


# register all client handlers
def register_client_handlers(dp: Dispatcher):
    dp.register_message_handler(start_command_handler, commands=['start', 'help'])
    dp.register_message_handler(location_button_handler, Text(equals='📍 Розташування'))
    dp.register_message_handler(regime_button_handler, Text(equals='🕑 Наш розклад'))
    dp.register_message_handler(catalog_button_handler, Text(equals='📜 Каталог'))
    dp.register_message_handler(user_orders_button_handler, Text(equals='🧾Мої замовлення'))
    dp.register_message_handler(cancel_button_handler, Text(equals='🚫 Скасувати'), state="*")
    handlers_order.register_client_order_handlers(dp)
