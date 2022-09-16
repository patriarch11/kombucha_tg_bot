import random
import time
import bot_messages
from aiogram import types, Dispatcher
from database import sqlite_bot
from aiogram.dispatcher.filters import Text
from . import keyboards
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import logging

client_logger = logging.getLogger('bot.client')
"""
creating new  order path
"""


# states for creating order
class OrderStates(StatesGroup):
    order_count = State()
    order_mailing_info = State()


# class for creating new order
class NewOrderClient:
    def __init__(self, id_prod: str, user_id: str):
        self.order_id = random.randint(10000, 99999)
        self.user_id = user_id
        self.id_prod = id_prod
        self.count = None
        self.total = None
        self.mailing_info = None
        self.time = time.ctime()
        self.status = 'new'

    def add_count(self, count: int) -> bool:
        available_count = sqlite_bot.get_info_about_prod('count', self.id_prod)
        client_logger.info(f'--------{available_count}-----------')
        if count <= available_count:
            self.count = count
            client_logger.info(f'-----------------{count}------------')
            return True
        else:
            return False

    def add_mailing_info(self, info: str):
        self.mailing_info = info

    def order_finish(self):
        sqlite_bot.divide_count_from_target_prod(self.id_prod, self.count)  # update storage table
        sqlite_bot.add_new_order_to_db(tuple(self.__dict__.values()))  # update order table #

    def get_total(self):
        prod_price = sqlite_bot.get_info_about_prod('price', self.id_prod)
        self.total = self.count * prod_price

    def __str__(self):
        return f'id замовлення: {self.order_id}\n' \
               f'id товару: {self.id_prod}\n' \
               f'к-ть: {self.count} pcs\n' \
               f'всього: {self.total} UAH\n' \
               f'буде доставлено: {self.mailing_info}\n' \
               f'дата замовлення: {self.time}'


# callback handler for start sell product
async def start_buy_product(callback_data: types.CallbackQuery):
    await callback_data.answer()
    global new_order
    new_order = NewOrderClient(callback_data.data.split(':')[1], callback_data.from_user.id)
    await OrderStates.order_count.set()
    await callback_data.message.answer('Введдіть к-ть товару, яку бажаєте придбати',
                                       reply_markup=keyboards.client_cancel_kb)


# add count to order info
async def add_count_to_order(message: types.Message, state: FSMContext):
    cnt = 0
    try:
        cnt = int(message)
    except Exception as ex:
        client_logger.error(f'[-] {ex}')
        await state.finish()
        await state.reset_data()
        await message.reply(bot_messages.adm_handlers_msgs['incorrect_value'], reply_markup=keyboards.client_kb)

    res = new_order.add_count(cnt)

    if res is True:
        await OrderStates.next()
        await message.reply('Введіть інфромацію для відправлення замовлення вам по пошті',
                            reply_markup=keyboards.client_cancel_kb)
    else:
        await state.finish()
        await state.reset_data()
        await message.reply('На даний мометн така к-ть товару не доступна, замовлення скасовано',
                            reply_markup=keyboards.client_kb)


# add mailing info to order info
async def add_mailing_info_to_order(message: types.Message, state: FSMContext):
    new_order.add_mailing_info(message.text)
    new_order.get_total()
    new_order.order_finish()
    await message.reply(str(new_order), reply_markup=keyboards.create_inline_order_btn(new_order.order_id))
    await message.reply('Здійсніть переказ на картку 1234-1234-1234-1234 та надішліть квитанцію оператору',
                        reply_markup=keyboards.client_kb)
    await state.finish()
    await state.reset_data()


"""
canceling order
"""


async def cancel_order(callback_data: types.CallbackQuery):
    await callback_data.answer()
    if sqlite_bot.find_order_by_id(callback_data.data.split(':')[1])[-1] == 'new':
        sqlite_bot.set_status_ord(callback_data.data.split(':')[1], 'canceled')
        prod = sqlite_bot.find_order_by_id(callback_data.data.split(':')[1])[2]
        count = sqlite_bot.find_order_by_id(callback_data.data.split(':')[1])[3]
        sqlite_bot.add_count_to_target_prod(prod, count)
        await callback_data.message.reply(f'{callback_data.data.split(":")[1]} скасовано')
    else:
        await callback_data.message.reply('Замовлення оплачене або скасоване, не можливо змінити статус')


# register handler for working with orders
def register_client_order_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(start_buy_product, Text(startswith='Buy'), state=None)
    dp.register_message_handler(add_count_to_order, state=OrderStates.order_count)
    dp.register_message_handler(add_mailing_info_to_order, state=OrderStates.order_mailing_info)

    dp.register_callback_query_handler(cancel_order, Text(startswith='CancOrd'))
