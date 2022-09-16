from aiogram import Bot, Dispatcher
from dotenv import find_dotenv, load_dotenv
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os

load_dotenv(find_dotenv())

# bot settings
TOKEN = os.getenv('TOKEN')
ADMIN_PASS = os.getenv('ADMIN_PASSWORD')
HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')
storage = MemoryStorage()
bot = Bot(token=TOKEN)
bot.admin_ID = None
dp = Dispatcher(bot=bot, storage=storage)


# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webapp settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.getenv('PORT', default=8000)
