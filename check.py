import logging
from datetime import date, timedelta

from bot import bot
from config import db_config, admin_id
from database.requests import DatabaseManager
from keyboards import keyboard_buy, keyboard_parts
from lexicon import lexicon
from photo.get_photo import get_photo

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
    now = date.today()
    users = await db_manager.get_users()
    for user in users:
        if user and user.end_date:
            logging.debug(f'Check_pay {user.user_id}')
            days = user.end_date
            end = days + timedelta(days=2)
            print(days, now, days==now)
            print(days, now, end, days < now < end)
            print(end, now, end == now)
            print(now, (end + timedelta(days=1)), (end + timedelta(days=1)) >= now)
            if days == now:
                await bot.send_photo(photo=get_photo(name=10), chat_id=user.user_id, caption=lexicon['pay'], reply_markup=keyboard_parts())
            elif days < now < end:
                await bot.send_photo(photo=get_photo(name=10), chat_id=user.user_id, caption=lexicon['pay_urgently'].format(day=days+1-now), reply_markup=keyboard_parts())
            elif end == now:
                await bot.send_photo(photo=get_photo(name=10), chat_id=user.user_id, caption=lexicon['day_9'],
                                 reply_markup=keyboard_parts())
            elif (end + timedelta(days=1)) <= now:
                await bot.send_photo(photo=get_photo(name=10), chat_id=user.user_id, caption=lexicon['del_user'])
                await bot.send_message(chat_id=admin_id(),
                                       text=lexicon['for_admin_4'].format(user_id=user.user_id,
                                                                          user_name=user.name,
                                                                          user_email=user.email,
                                                                          user_phone=user.phone))
                await db_manager.delete_user(user_id=user.user_id)
                logging.debug(f'Kick user by id={user.user_id}')


async def check_link():
    d = {True: 'Договоры для Совершеннолетних', False: 'Договоры для Несовершеннолетних'}
    for key, item in d.items():
        links = await db_manager.get_links(status=key)
        logging.debug(f'Check_link')
        if links == []:
            await bot.send_message(chat_id=admin_id(), text=lexicon['new_links'].format(button=item))
