from create_bot import bot
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import sqlite_bot
from aiogram.dispatcher.filters import Text
from . import keyboards

"""
functions for operations from order keyboard
"""


# state for find order by id
class OrderStates(StatesGroup):
    find_state = State()


# show orders with status new
async def show_new_orders(message: types.Message):
    if message.from_user.id == bot.admin_ID:
        for order in sqlite_bot.find_order_by_status('new'):
            await bot.send_message(bot.admin_ID, f'order_id: {order[0]}\nuser_id: {order[1]}\n'
                                                 f'product_id: {order[2]}\n'
                                                 f'count {order[3]} pcs\n'
                                                 f'total: {order[4]}\n'
                                                 f'mailing_info: {order[5]}\n'
                                                 f'date: {order[6]}\n'
                                                 f'status: {order[7]}',
                                   reply_markup=keyboards.create_order_inline_admin_kb(order[0]))
        await message.delete()


# show orders with status paid
async def show_paid_orders(message: types.Message):
    if message.from_user.id == bot.admin_ID:
        for order in sqlite_bot.find_order_by_status('paid'):
            await bot.send_message(bot.admin_ID, f'order_id: {order[0]}\nuser_id: {order[1]}\n'
                                                 f'product_id: {order[2]}\n'
                                                 f'count {order[3]} pcs\n'
                                                 f'total: {order[4]}\n'
                                                 f'mailing_info: {order[5]}\n'
                                                 f'date: {order[6]}\n'
                                                 f'status: {order[7]}',
                                   reply_markup=keyboards.create_order_inline_admin_kb(order[0]))
        await message.delete()


# show orders with status canceled
async def show_canceled_orders(message: types.Message):
    if message.from_user.id == bot.admin_ID:
        for order in sqlite_bot.find_order_by_status('canceled'):
            await bot.send_message(bot.admin_ID, f'order_id: {order[0]}\nuser_id: {order[1]}\n'
                                                 f'product_id: {order[2]}\n'
                                                 f'count {order[3]} pcs\n'
                                                 f'total: {order[4]}\n'
                                                 f'mailing_info: {order[5]}\n'
                                                 f'date: {order[6]}\n'
                                                 f'status: {order[7]}',
                                   reply_markup=keyboards.create_order_inline_admin_kb(order[0]))
        await message.delete()


# start finding order by id
async def start_find_by_id(message: types.Message):
    if message.from_user.id == bot.admin_ID:
        await OrderStates.find_state.set()
        await message.reply('Введіть id замовлення', reply_markup=keyboards.admin_kb_cancel)


# show order by id
async def find_by_id(message: types.Message, state: FSMContext):
    if message.from_user.id == bot.admin_ID:
        order = None
        try:
            finding_id = int(message.text)
            order = sqlite_bot.find_order_by_id(finding_id)
        except Exception:
            pass
        if order:
            await message.reply(f'order_id: {order[0]}\nuser_id: {order[1]}\n'
                                f'product_id: {order[2]}\n'
                                f'count {order[3]} pcs\n'
                                f'total: {order[4]}\n'
                                f'mailing_info: {order[5]}\n'
                                f'date: {order[6]}\n'
                                f'status: {order[7]}',
                                reply_markup=keyboards.create_order_inline_admin_kb(order[0]))
            await message.reply('+', reply_markup=keyboards.admin_kb_orders)
        else:
            await message.reply(f'{finding_id} не знайдено', reply_markup=keyboards.admin_kb_orders)
        await state.finish()
        await state.reset_data()


"""
functions for operations from inline kb
"""


# inline handler for delete order button
async def delete_order(callback_data: types.CallbackQuery):
    if callback_data.from_user.id == bot.admin_ID:
        await callback_data.answer()
        if sqlite_bot.find_order_by_id(callback_data.data.split(':')[1])[7] != 'new':
            sqlite_bot.delete_order(callback_data.data.split(':')[1])
            await callback_data.message.answer(f'[+] {callback_data.data.split(":")[1]} видалено')
        else:
            await callback_data.message.reply('Неможливо видалити нове замовлення, скасуйте або сплатіть')


# inline handler for pay order button
async def pay_order(callback_data: types.CallbackQuery):
    if callback_data.from_user.id == bot.admin_ID:
        await callback_data.answer()
        if sqlite_bot.find_order_by_id(callback_data.data.split(':')[1])[-1] == 'new':
            sqlite_bot.set_status_ord(callback_data.data.split(':')[1], 'paid')
            await callback_data.message.answer(f'{callback_data.data.split(":")[1]} cплачено')
        else:
            await callback_data.message.reply('Замовлення оплачене або скасоване, не можливо змінити статус')


# inline handler for cancel order button
async def cancel_order(callback_data: types.CallbackQuery):
    if callback_data.from_user.id == bot.admin_ID:
        await callback_data.answer()
        if sqlite_bot.find_order_by_id(callback_data.data.split(':')[1])[-1] == 'new':
            sqlite_bot.set_status_ord(callback_data.data.split(':')[1], 'canceled')
            prod = sqlite_bot.find_order_by_id(callback_data.data.split(':')[1])[2]
            count = sqlite_bot.find_order_by_id(callback_data.data.split(':')[1])[3]
            sqlite_bot.add_count_to_target_prod(prod, count)
            await callback_data.message.reply(f'{callback_data.data.split(":")[1]} скасовано')
        else:
            await callback_data.message.reply('Замовлення оплачене або скасоване, не можливо змінити статус')


# register all admin handlers for work with orders
def register_admin_orders_handlers(dp: Dispatcher):
    # handlers from order keyboard
    dp.register_message_handler(show_new_orders, Text(equals='#📩Нові'))
    dp.register_message_handler(show_paid_orders, Text(equals='#✅Оплачені'))
    dp.register_message_handler(show_canceled_orders, Text(equals='#⛔Скасовані'))
    dp.register_message_handler(start_find_by_id, Text(equals='🔍ID'), state=None)
    dp.register_message_handler(find_by_id, state=OrderStates.find_state)
    # inline handlers
    dp.register_callback_query_handler(delete_order, Text(startswith='OrdDel'))
    dp.register_callback_query_handler(pay_order, Text(startswith='Paid'))
    dp.register_callback_query_handler(cancel_order, Text(startswith='OrdCancel'))
