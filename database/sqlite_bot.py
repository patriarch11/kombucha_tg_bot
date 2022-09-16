import sqlite3
import logging

from bot_messages import *

"""
sql start block
"""

connect = sqlite3.connect('kombucha_store.db')
cur = connect.cursor()
db_logger = logging.getLogger('bot.sql_db')


# start work with sql database
def database_start():
    # creating tables if not exist
    try:
        # products storage table
        connect.execute('CREATE TABLE IF NOT EXISTS storage(img TEXT, id TEXT primary key, name TEXT, '
                        'description TEXT, price REAL, count INTEGER)')
        # bot messages table
        connect.execute('CREATE TABLE IF NOT EXISTS bot_texts(start_text TEXT, start_img TEXT, help TEXT,'
                        'location TEXT, regime TEXT)')
        # orders table
        connect.execute('CREATE TABLE IF NOT EXISTS orders(id INTEGER primary key, user_id TEXT, prod_id TEXT, '
                        'count INTEGER, total REAL, address TEXT, time TEXT, status TEXT)')
        connect.commit()
        set_default_bot_messages()
        db_logger.debug('[+] Tables created successfully')
    except Exception as ex:
        db_logger.error(f'[-] {ex}')


#  set default messages for start, help etc. command
def set_default_bot_messages():
    cur.execute('INSERT INTO bot_texts VALUES(?, ?, ?, ?, ?)',
                (default_messages['start_msg'], default_messages['start_img'], default_messages['help_msg'],
                 default_messages['location_msg'], default_messages['regime_msg']))
    connect.commit()


"""
funcs for table storage
"""


# load new product to storage
def load_new_prod(prod_values: tuple):
    try:
        cur.execute('INSERT INTO storage VALUES(?, ?, ?, ?, ?, ?)', prod_values)
        connect.commit()
        db_logger.info(f'[+] Added {prod_values} to storage')
    except Exception as ex:
        db_logger.error(f'[-] {ex}')


# get product with not null count from storage
def select_catalog():
    for product in cur.execute('SELECT * FROM storage').fetchall():
        if product[-1] < 1:
            continue
        yield product
    return


# get product with 0 count from storage
def select_zero_count():
    for product in cur.execute('SELECT * FROM storage').fetchall():
        if product[-1] < 1:
            yield product
    return


# get any info about product
def get_info_about_prod(param: str, prod_id: str) -> int | float | str:
    return cur.execute(f'SELECT {param} FROM storage WHERE id = "{prod_id}"').fetchone()[0]


# divide count from target product
def divide_count_from_target_prod(prod_id: str, count: int):
    cur.execute(f'UPDATE storage SET count = count - {count} WHERE id = "{prod_id}"')
    connect.commit()
    db_logger.info(f'[+] Divide {count} pcs from {prod_id}')


# add count to target product
def add_count_to_target_prod(prod_id: str, count: int):
    cur.execute(f'UPDATE storage SET count = count + {count} WHERE id = "{prod_id}"')
    connect.commit()
    db_logger.info(f'[+] Added {count} pcs to {prod_id}')


# delete product from storage
def delete_product_from_db(prod_id: str):
    cur.execute(f'DELETE FROM storage WHERE id ="{prod_id}"')
    connect.commit()
    db_logger.info(f'[+] Deleted {prod_id} from storage')


# edit any text info about product
def edit_prod_text_info(prod_id: str, param: str, new_value: str):
    try:
        cur.execute(f'UPDATE storage SET {param} = "{new_value}" WHERE id = "{prod_id}"')
        connect.commit()
        db_logger.info(f'[+] New value {param} for {prod_id}  = {new_value}')
    except Exception as ex:
        db_logger.error(f'[-] {ex}')


def edit_target_price(prod_id: str, price: float):
    try:
        cur.execute(f'UPDATE storage SET price = {price} WHERE id = "{prod_id}"')
        connect.commit()
        db_logger.info(f'[+] New price for {prod_id} is {price} UAH')
    except Exception as ex:
        db_logger.error(f'[-] {ex}')


"""
functions for table orders
"""


def add_new_order_to_db(order_data: tuple):
    try:
        cur.execute('INSERT INTO orders VALUES(?, ?, ?, ?, ?, ?, ?, ?)', order_data)
        connect.commit()
        db_logger.info(f'[+] Added new order {order_data}')
    except Exception as ex:
        db_logger.error(f'[-] {ex}')


def set_status_ord(order_id: int, new_status: str):
    try:
        cur.execute(f'UPDATE orders SET status = "{new_status}" WHERE id = {order_id}')
        connect.commit()
        db_logger.info(f'[+] New status for {order_id} is {new_status}')
    except Exception as ex:
        db_logger.info(f'[-] {ex}')


# find order by id
def find_order_by_id(order_id: int) -> tuple:
    try:
        return cur.execute(f'SELECT * FROM orders WHERE id = {order_id}').fetchone()
    except Exception as ex:
        db_logger.error(f'[-] {ex}')


# find order by status
def find_order_by_status(status=None):
    if status:
        for order in cur.execute(f'SELECT * FROM orders WHERE status = "{status}"').fetchall():
            yield order
        return
    else:
        for order in cur.execute(f'SELECT * FROM orders').fetchall():
            yield order
        return


def find_order_by_user(user_id: str) -> tuple:
    try:
        for order in cur.execute(f'SELECT * FROM orders WHERE user_id = "{user_id}"').fetchall():
            yield order
        return
    except Exception as ex:
        db_logger.error(f'[-] {ex}')


# delete order from db
def delete_order(order_id):
    try:
        cur.execute(f'DELETE FROM orders WHERE id = "{order_id}"')
        connect.commit()
        db_logger.info(f'[+] Deleted order {order_id}')
    except Exception as ex:
        db_logger.error(f'[-] {ex}')


"""
functions for table bot_texts
"""


# get any param from table bot texts, this funcs return bot messages like a start message, etc
def get_param_from_bt(param: str) -> str:
    return cur.execute(f'SELECT {param} FROM bot_texts').fetchone()[0]


# edit bot messages: start, help, etc.
def edit_bot_message(message_type: str, new_message: str):
    cur.execute(f'UPDATE bot_texts SET {message_type} = "{new_message}"')
    connect.commit()
    db_logger.info(f'[+] New value for {message_type} is {new_message}')
