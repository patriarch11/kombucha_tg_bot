from create_bot import bot
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import sqlite_bot
from aiogram.dispatcher.filters import Text
from . import keyboards


# class for work with edited prod
class EditedProd:
    def __init__(self, prod_id: str):
        self.prod_id = prod_id

    def add_count(self, count):
        sqlite_bot.add_count_to_target_prod(self.prod_id, count)

    def divide_count(self, count):
        sqlite_bot.divide_count_from_target_prod(self.prod_id, count)

    def check_count(self) -> int:
        return sqlite_bot.get_info_about_prod('count', self.prod_id)

    def change_text_param(self, param: str, new_value: str):
        sqlite_bot.edit_prod_text_info(self.prod_id, param, new_value)

    def change_price(self, price: float):
        sqlite_bot.edit_target_price(self.prod_id, price)


# states for edit product value
class EditStates(StatesGroup):
    add_state = State()
    divide_state = State()
    edit_img_state = State()
    edit_name_state = State()
    edit_description_state = State()
    edit_price_state = State()


# delete product from db(inline button handler)
async def delete_prod(callback_data: types.CallbackQuery):
    if callback_data.from_user.id == bot.admin_ID:
        await callback_data.answer()
        sqlite_bot.delete_product_from_db(callback_data.data.split(':')[1])
        await callback_data.message.answer(f'[+] Видалено {callback_data.data.split(":")[1]}')


# start adding count to  target product
async def add_target_count_start(callback_data: types.CallbackQuery):
    if callback_data.from_user.id == bot.admin_ID:
        await callback_data.answer()
        await EditStates.add_state.set()
        global add_cnt_prod
        add_cnt_prod = EditedProd(callback_data.data.split(':')[1])
        await callback_data.message.answer(f'Введіть к-ть id:{callback_data.data.split(":")[1]}',
                                           reply_markup=keyboards.admin_kb_cancel)


# catching count and add count to target product
async def add_target_count(message: types.Message, state: FSMContext):
    if message.from_user.id == bot.admin_ID:
        async with state.proxy() as data:
            cnt = int(message.text)
        add_cnt_prod.add_count(cnt)
        await state.finish()
        await state.reset_data()
        await message.reply(f'[+] Додано {cnt} од.', reply_markup=keyboards.admin_kb_start)


# start dividing count from target product
async def divide_target_count_start(callback_data: types.CallbackQuery):
    if callback_data.from_user.id == bot.admin_ID:
        await EditStates.divide_state.set()
        await callback_data.answer()
        global div_cnt_prod
        div_cnt_prod = EditedProd(callback_data.data.split(':')[1])
        await callback_data.message.answer(f'Введіть к-ть id:{callback_data.data.split(":")[1]}',
                                           reply_markup=keyboards.admin_kb_cancel)


# catching count for divide and divide count from target count
async def divide_target_count(message: types.Message, state: FSMContext):
    if message.from_user.id == bot.admin_ID:
        async with state.proxy() as data:
            cnt = int(message.text)
        if cnt <= div_cnt_prod.check_count():  # checking count for 0
            div_cnt_prod.divide_count(cnt)
            await state.finish()
            await state.reset_data()
            await message.reply(f'[+] Зменшено на {cnt} од.', reply_markup=keyboards.admin_kb_start)
        else:
            await state.finish()
            await state.reset_data()
            await message.reply(f'[-] Значення к-ті не може бути менше 0', reply_markup=keyboards.admin_kb_start)


# start edit img for target product
async def img_start_edit(callback_data: types.CallbackQuery):
    if callback_data.from_user.id == bot.admin_ID:
        await callback_data.answer()
        await EditStates.edit_img_state.set()
        global img_ed_prod
        img_ed_prod = EditedProd(callback_data.data.split(':')[1])
        await callback_data.message.reply(f'Завантажте нове фото id:{callback_data.data.split(":")[1]}',
                                          reply_markup=keyboards.admin_kb_cancel)


# catching new img and update this value in database
async def img_edit(message: types.Message, state: FSMContext):
    if message.from_user.id == bot.admin_ID:
        new_img = message.photo[0].file_id
        img_ed_prod.change_text_param('img', new_img)
        await state.finish()
        await state.reset_data()
        await message.reply('[+] Фото змінено', reply_markup=keyboards.admin_kb_start)


# start edit name for target product
async def name_edit_start(callback_data: types.CallbackQuery):
    if callback_data.from_user.id == bot.admin_ID:
        await callback_data.answer()
        await EditStates.edit_name_state.set()
        global name_ed_prod
        name_ed_prod = EditedProd(callback_data.data.split(':')[1])
        await callback_data.message.answer(f'Введіть нову назву id:{callback_data.data.split(":")[1]}',
                                           reply_markup=keyboards.admin_kb_cancel)


# catching new name for target product and update this value in database
async def name_edit(message: types.Message, state: FSMContext):
    if message.from_user.id == bot.admin_ID:
        name_ed_prod.change_text_param('name', message.text)
        await state.finish()
        await state.reset_data()
        await message.reply('[+] Назву змінено', reply_markup=keyboards.admin_kb_start)


# start editing description for target product
async def description_edit_start(callback_data: types.CallbackQuery):
    if callback_data.from_user.id == bot.admin_ID:
        await callback_data.answer()
        await EditStates.edit_description_state.set()
        global desc_ed_prod
        desc_ed_prod = EditedProd(callback_data.data.split(':')[1])
        await callback_data.message.answer(f'Введіть новий опис id:{callback_data.data.split(":")[1]}',
                                           reply_markup=keyboards.admin_kb_cancel)


# catching new description and update this value in db
async def description_edit(message: types.Message, state: FSMContext):
    if message.from_user.id == bot.admin_ID:
        desc_ed_prod.change_text_param('description', message.text)
        await state.finish()
        await state.reset_data()
        await message.reply('Опис змінено', reply_markup=keyboards.admin_kb_start)


# start setting new price for target product
async def price_edit_start(callback_data: types.CallbackQuery):
    if callback_data.from_user.id == bot.admin_ID:
        await callback_data.answer()
        await EditStates.edit_price_state.set()
        global price_ed_prod
        price_ed_prod = EditedProd(callback_data.data.split(':')[1])
        await callback_data.message.answer(f'Введіть нову ціну id:{callback_data.data.split(":")[1]}',
                                           reply_markup=keyboards.admin_kb_cancel)


# catching new price and update this value in database
async def price_edit(message: types.Message, state: FSMContext):
    if message.from_user.id == bot.admin_ID:
        new_price = float(message.text)
        price_ed_prod.change_price(new_price)
        await state.finish()
        await state.reset_data()
        await message.reply('Ціну змінено', reply_markup=keyboards.admin_kb_start)


# register all handler for operation with product cart
def register_admin_product_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(delete_prod, Text(startswith='Delete'))

    dp.register_callback_query_handler(add_target_count_start, Text(startswith='Add'), state=None)
    dp.register_message_handler(add_target_count, state=EditStates.add_state)

    dp.register_callback_query_handler(divide_target_count_start, Text(startswith='Div'), state=None)
    dp.register_message_handler(divide_target_count, state=EditStates.divide_state)

    dp.register_callback_query_handler(img_start_edit, Text(startswith='ImgEdit'), state=None)
    dp.register_message_handler(img_edit, content_types='photo', state=EditStates.edit_img_state)

    dp.register_callback_query_handler(name_edit_start, Text(startswith='NameEdit'), state=None)
    dp.register_message_handler(name_edit, state=EditStates.edit_name_state)

    dp.register_callback_query_handler(description_edit_start, Text(startswith='DescEdit'), state=None)
    dp.register_message_handler(description_edit, state=EditStates.edit_description_state)

    dp.register_callback_query_handler(price_edit_start, Text(startswith='PriceEdit'), state=None)
    dp.register_message_handler(price_edit, state=EditStates.edit_price_state)
