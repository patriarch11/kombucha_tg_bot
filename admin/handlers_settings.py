from aiogram import types, Dispatcher
from . import keyboards
from create_bot import bot
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from database import sqlite_bot


# states for settings
class Settings(StatesGroup):
    start_img_state = State()
    start_text_state = State()
    help_state = State()
    location_state = State()
    regime_state = State()


# start editing img from start message
async def start_edit_start_img(message: types.Message):
    if message.from_user.id == bot.admin_ID:
        await Settings.start_img_state.set()
        await bot.send_message(bot.admin_ID, 'Завантажте нове фото', reply_markup=keyboards.admin_kb_cancel)
        await message.delete()


# edit img from start message
async def edit_start_img(message: types.Message, state: FSMContext):
    if message.from_user.id == bot.admin_ID:
        new_img = message.photo[0].file_id
        sqlite_bot.edit_bot_message('start_img', new_img)
        await state.finish()
        await state.reset_data()
        await message.reply('[+] Стартове фото змінено', reply_markup=keyboards.admin_kb_settings)


# start edit text from start message
async def start_edit_start_txt(message: types.Message):
    if message.from_user.id == bot.admin_ID:
        await Settings.start_text_state.set()
        await bot.send_message(bot.admin_ID, 'Вкажіть новий текст', reply_markup=keyboards.admin_kb_cancel)
        await message.delete()


# edit text from start message
async def edit_start_txt(message: types.Message, state: FSMContext):
    if message.from_user.id == bot.admin_ID:
        sqlite_bot.edit_bot_message('start_text', message.text)
        await state.finish()
        await state.reset_data()
        await message.reply('[+] Старотовий текст змінено', reply_markup=keyboards.admin_kb_settings)


# start edit help message
async def start_edit_help_mgs(message: types.Message):
    if message.from_user.id == bot.admin_ID:
        await Settings.help_state.set()
        await bot.send_message(bot.admin_ID, 'Вкажіть нове хелп повідомлення', reply_markup=keyboards.admin_kb_cancel)
        await message.delete()


# edit help message
async def edit_help_msg(message: types.Message, state: FSMContext):
    if message.from_user.id == bot.admin_ID:
        sqlite_bot.edit_bot_message('help', message.text)
        await state.finish()
        await state.reset_data()
        await message.reply('[+] Хелп повідомлення змінено', reply_markup=keyboards.admin_kb_settings)


# start editing regime message
async def start_edit_regime_msg(message: types.Message):
    if message.from_user.id == bot.admin_ID:
        await Settings.regime_state.set()
        await bot.send_message(bot.admin_ID, 'Вкажіть новий режим', reply_markup=keyboards.admin_kb_cancel)
        await message.delete()


# edit regime message
async def edit_regime_msg(message: types.Message, state: FSMContext):
    if message.from_user.id == bot.admin_ID:
        sqlite_bot.edit_bot_message('regime', message.text)
        await state.finish()
        await state.reset_data()
        await message.reply('[+] Режим змінений', reply_markup=keyboards.admin_kb_settings)


# start edit location message
async def start_edit_location_msg(message: types.Message):
    if message.from_user.id == bot.admin_ID:
        await Settings.location_state.set()
        await bot.send_message(bot.admin_ID, 'Вкажіть нове розташування', reply_markup=keyboards.admin_kb_cancel)


# edit location message
async def edit_location_msg(message: types.Message, state: FSMContext):
    if message.from_user.id == bot.admin_ID:
        sqlite_bot.edit_bot_message('location', message.text)
        await state.finish()
        await state.reset_data()
        await message.reply('[+] Розташування змінено', reply_markup=keyboards.admin_kb_settings)


# register settings handlers
def register_setting_handlers(dp: Dispatcher):
    dp.register_message_handler(start_edit_start_img, Text(equals='✏️Стартове фото'), state=None)
    dp.register_message_handler(edit_start_img, content_types='photo', state=Settings.start_img_state)
    dp.register_message_handler(start_edit_start_txt, Text(equals='✏️Стартовий текст'), state=None)
    dp.register_message_handler(edit_start_txt, state=Settings.start_text_state)
    dp.register_message_handler(start_edit_help_mgs, Text(equals='❔Змінити хелп повідомлення'), state=None)
    dp.register_message_handler(edit_help_msg, state=Settings.help_state)
    dp.register_message_handler(start_edit_regime_msg, Text(equals='🕑Змінити режим'), state=None)
    dp.register_message_handler(edit_regime_msg, state=Settings.regime_state)
    dp.register_message_handler(start_edit_location_msg, Text(equals='📍Змінити розташування'), state=None)
    dp.register_message_handler(edit_location_msg, state=Settings.location_state)
