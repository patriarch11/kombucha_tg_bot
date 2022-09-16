from create_bot import bot
from aiogram import Dispatcher, types
from create_bot import ADMIN_PASS
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import logging
import re
import bot_messages
from database import sqlite_bot
from aiogram.dispatcher.filters import Text
from . import keyboards, handlers_settings, handlers_product, handlers_orders
from client import keyboards as ck

# current admin id
admin_logger = logging.getLogger('bot.admin')


# login to admin account
async def get_admin_tools(message: types.Message):
    if message.text.split(' ')[1] == ADMIN_PASS:
        bot.admin_ID = message.from_user.id
        await bot.send_message(bot.admin_ID, 'Admin account activated', reply_markup=keyboards.admin_kb_start)
        admin_logger.info(f'[+] Current admin is {bot.admin_ID}')
    else:
        await bot.send_message(message.from_user.id, '[-] Wrong password')
        admin_logger.info(f'[!] User {message.from_user.id} input wrong passwd')
    await message.delete()


"""
main admin functions
"""


# handler for cancel any state
async def cancel_button_handler(message: types.Message, state: FSMContext):
    if message.from_user.id == bot.admin_ID:
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        await state.reset_data()
        await message.reply('Cкасовано', reply_markup=keyboards.admin_kb_start)


# handler for exit from admin account
async def exit_button_handler(message: types.Message):
    if message.from_user.id == bot.admin_ID:
        bot.admin_ID = None
        admin_logger.info(f'[-] User {message.from_user.id} exit from admin account')
        await bot.send_message(message.from_user.id, '[-] Вихід з адмін акаунту', reply_markup=ck.client_kb)
        await message.delete()


# handler for settings button
async def settings_button_handler(message: types.Message):
    if message.from_user.id == bot.admin_ID:
        await bot.send_message(bot.admin_ID, bot_messages.adm_handlers_msgs['bot_settings'],
                               reply_markup=keyboards.admin_kb_settings)
        await message.delete()


# handler for orders button
async def orders_button_handler(message: types.Message):
    if message.from_user.id == bot.admin_ID:
        await bot.send_message(bot.admin_ID, bot_messages.adm_handlers_msgs['orders'],
                               reply_markup=keyboards.admin_kb_orders)
        await message.delete()


# handler for catalog button, show all product where count not 0
async def catalog_button_handler(message: types.Message):
    if message.from_user.id == bot.admin_ID:
        for product in sqlite_bot.select_catalog():
            await bot.send_photo(bot.admin_ID, product[0], f'id: {product[1]}\nname: {product[2]}\n'
                                                           f'description:\n{product[3]}'
                                                           f'\nprice: {product[4]} UAH\ncount: {product[5]} pcs',
                                 reply_markup=keyboards.create_inline_admin_kb(product[1]))
        await message.delete()


# handler for showing product where count = 0
async def zero_count_button_handler(message: types.Message):
    if message.from_user.id == bot.admin_ID:
        for product in sqlite_bot.select_zero_count():
            await bot.send_photo(bot.admin_ID, product[0],
                                 f'id: {product[1]}\nname: {product[2]}\ndescription:\n{product[3]}'
                                 f'\nprice: {product[4]} UAH\ncount: {product[5]} pcs',
                                 reply_markup=keyboards.create_inline_admin_kb(product[1]))
        await message.delete()


# handler for back button
async def back_button_handler(message: types.Message):
    if message.from_user.id == bot.admin_ID:
        await bot.send_message(bot.admin_ID, 'Назад', reply_markup=keyboards.admin_kb_start)
        await message.delete()


"""
load new product functions
"""


# load states
class LoadStates(StatesGroup):
    new_img = State()
    new_id = State()
    new_name = State()
    new_description = State()
    new_price = State()
    new_count = State()


# start loading handler
async def start_load_new_prod(message: types.Message):
    if message.from_user.id == bot.admin_ID:
        await LoadStates.new_img.set()
        await bot.send_message(bot.admin_ID, 'Завантажте фото товару', reply_markup=keyboards.admin_kb_cancel)
        await message.delete()


# get img for new product
async def load_img(message: types.Message, state: FSMContext):
    if message.from_user.id == bot.admin_ID:
        async with state.proxy() as data:
            data['img'] = message.photo[0].file_id
        await LoadStates.next()
        await message.reply('Відправте id товару 5 цифр')


# get id for new product
async def load_id(message: types.Message, state: FSMContext):
    if message.from_user.id == bot.admin_ID:
        if re.fullmatch(r'\d{5}', message.text):
            async with state.proxy() as data:
                data['prod_id'] = message.text
            await LoadStates.next()
            await message.reply('Вкажіть назву товару')
        else:
            await state.finish()
            await state.reset_data()
            await message.reply(bot_messages.adm_handlers_msgs['incorrect_value'],
                                reply_markup=keyboards.admin_kb_start)


# get name for new product
async def load_name(message: types.Message, state: FSMContext):
    if message.from_user.id == bot.admin_ID:
        async with state.proxy() as data:
            data['name'] = message.text
        await LoadStates.next()
        await message.reply('Вкажіть опис товару')


# get description for new product
async def load_description(message: types.Message, state: FSMContext):
    if message.from_user.id == bot.admin_ID:
        async with state.proxy() as data:
            data['description'] = message.text
        await LoadStates.next()
        await message.reply('Вкажіть ціну товару')


# get price for new product
async def load_price(message: types.Message, state: FSMContext):
    if message.from_user.id == bot.admin_ID:
        if re.fullmatch(r'[^0, \D]\d+.?\d*', message.text):
            async with state.proxy() as data:
                try:
                    data['price'] = float(message.text)
                except Exception:
                    await state.finish()
                    await state.reset_data()
                    await message.reply(bot_messages.adm_handlers_msgs['incorrect_value'],
                                        reply_markup=keyboards.admin_kb_start)
            await LoadStates.next()
            await message.reply('Вкажіть к-ть доданого товару')
        else:
            await state.finish()
            await state.reset_data()
            await message.reply(bot_messages.adm_handlers_msgs['incorrect_value'],
                                reply_markup=keyboards.admin_kb_start)


# get count for new product & finish load state
async def load_count(message: types.Message, state: FSMContext):
    if message.from_user.id == bot.admin_ID:
        if re.fullmatch(r'[^0, \D]\d+', message.text):
            async with state.proxy() as data:
                try:
                    data['count'] = int(message.text)
                except Exception:
                    await state.finish()
                    await state.reset_data()
                    await message.reply(bot_messages.adm_handlers_msgs['incorrect_value'],
                                        reply_markup=keyboards.admin_kb_start)
            await insert_new_prod_to_db(tuple(data.values()))
            await state.finish()
            await state.reset_data()
        else:
            await state.finish()
            await state.reset_data()
            await message.reply(bot_messages.adm_handlers_msgs['incorrect_value'],
                                reply_markup=keyboards.admin_kb_start)


# insert product to database
async def insert_new_prod_to_db(prod_values: tuple):
    sqlite_bot.load_new_prod(prod_values)
    await bot.send_photo(bot.admin_ID, prod_values[0], f' Додано:\nid: {prod_values[1]}\nname: {prod_values[2]}\n'
                                                       f'description:\n{prod_values[3]}\nprice: {prod_values[4]} UAH\n'
                                                       f'count: {prod_values[5]} pcs',
                         reply_markup=keyboards.admin_kb_start)


def register_admin_handlers(dp: Dispatcher):
    # main admin handlers
    dp.register_message_handler(get_admin_tools, commands='moder')
    dp.register_message_handler(cancel_button_handler, Text(equals='⭕ Скасувати'), state="*")
    dp.register_message_handler(exit_button_handler, Text(equals='🚪Вийти'))
    dp.register_message_handler(settings_button_handler, Text(equals='⚙️Налаштування'))
    dp.register_message_handler(orders_button_handler, Text(equals='🧾Замовлення'))
    dp.register_message_handler(catalog_button_handler, Text(equals='🛒Всі товари'))
    dp.register_message_handler(zero_count_button_handler, Text(equals='📖Які товари закінчились?'))
    dp.register_message_handler(back_button_handler, Text(equals='⬅️Назад'))
    # load new product handlers
    dp.register_message_handler(start_load_new_prod, Text(equals='⬆️ Завантажити'), state=None)
    dp.register_message_handler(load_img, content_types='photo', state=LoadStates.new_img)
    dp.register_message_handler(load_id, state=LoadStates.new_id)
    dp.register_message_handler(load_name, state=LoadStates.new_name)
    dp.register_message_handler(load_description, state=LoadStates.new_description)
    dp.register_message_handler(load_price, state=LoadStates.new_price)
    dp.register_message_handler(load_count, state=LoadStates.new_count)
    # settings handlers
    handlers_settings.register_setting_handlers(dp)
    # product changes handlers
    handlers_product.register_admin_product_handlers(dp)
    # orders handlers
    handlers_orders.register_admin_orders_handlers(dp)