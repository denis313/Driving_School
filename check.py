import logging
from datetime import date

from bot import bot
from config import db_config, admin_id
from database.requests import DatabaseManager
from keyboards import keyboard_buy, keyboard_parts
from lexicon import lexicon

logger = logging.getLogger(__name__)
dsn = db_config()
db_manager = DatabaseManager(dsn=dsn)


# async def check_pay():
#     logging.debug(f'Check_pay')
#     now = date.today()
#     users = await db_manager.get_users()
#     for user in users:
#         days = date_user - now
#         if days.days == 3:
#             await bot.send_message(chat_id=user.user_id, text=lexicon['pay'], reply_markup=keyboard_parts)
#         elif days.days + 10 == 9:
#             await bot.send_message(chat_id=user.user_id, text=lexicon['day_9'], reply_markup=keyboard_parts)
#         elif days.days + 10 == 10:
#             await bot.send_message(chat_id=user.user_id, text=lexicon['del_user'], reply_markup=keyboard_buy)
#             await db_manager.delete_user(user_id=user.user_id)
#             logging.debug(f'Kick user by id={user.user_id}')


async def check_pay():
    logging.debug(f'Check_pay')
    now = date.today()
    users = await db_manager.get_users()
    for user in users:
        if user:
            date_user = user.end_date
            days = date_user - now
            if days.days == 1:
                await bot.send_message(chat_id=user.user_id, text=lexicon['pay'], reply_markup=keyboard_parts)
            elif days.days + 1 == 2:
                await bot.send_message(chat_id=user.user_id, text=lexicon['day_9'], reply_markup=keyboard_parts)
            elif days.days + 1 == 3:
                await bot.send_message(chat_id=user.user_id, text=lexicon['del_user'], reply_markup=keyboard_buy)
                await db_manager.delete_user(user_id=user.user_id)
                logging.debug(f'Kick user by id={user.user_id}')


async def check_link():
    logging.debug(f'Check_link')
    d = {True: 'Договоры для Совершеннолетних', False: 'Договоры для Несовершеннолетних'}
    for key, item in d.items():
        links = await db_manager.get_links(status=key)
        if links is None:
            await bot.send_message(chat_id=admin_id(), text=lexicon['new_links'].format(button=item))
