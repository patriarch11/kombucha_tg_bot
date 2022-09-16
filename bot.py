import logging
from aiogram.utils.executor import start_webhook
from create_bot import dp, WEBHOOK_URL, bot, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT
from client import handlers_main as ch
from admin import handlers_main as ah
from database import sqlite_bot


# create logger
def init_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()  # stream handler for logger
    sh.setLevel(logging.DEBUG)
    sh.setFormatter(logging.Formatter('%(asctime)s : %(name)s : %(levelname)s --- %(message)s'))
    logger.addHandler(sh)
    logger.debug('[+] Logger initialized successfully')


# startup function
async def on_startup(_):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    init_logger('bot')
    root_logger = logging.getLogger('bot.root')
    root_logger.debug('[+] Bot is online')
    sqlite_bot.database_start()
    ch.register_client_handlers(dp)
    ah.register_admin_handlers(dp)


# shutdown function
async def on_shutdown(_):
    await bot.delete_webhook()


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
