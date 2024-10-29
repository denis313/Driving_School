import logging
from datetime import date, timedelta

from bot import bot
from config import db_config, admin_id
from database.requests import DatabaseManager
from keyboards import keyboard_buy, keyboard_parts, keyboard_friend
from lexicon import lexicon
from service import get_photo

logger = logging.getLogger(__name__)
dsn = db_config()
db_manager = DatabaseManager(dsn=dsn)


async def check_pay():
    now = date.today()
    users = await db_manager.get_users()
    for user in users:
        if user and user.end_date:
            logging.debug(f'Check_pay {user.user_id}')
            days = user.end_date
            end = days + timedelta(days=9)
            if days == now:
                await bot.send_photo(photo=get_photo(name='buy'), chat_id=user.user_id, caption=lexicon['pay'], reply_markup=keyboard_parts())
            elif days < now < end:
                await bot.send_photo(photo=get_photo(name='buy'), chat_id=user.user_id,
                                     caption=lexicon['pay_urgently'].format(day=(end+timedelta(days=1)-now).days), reply_markup=keyboard_parts())
            elif end == now:
                await bot.send_photo(photo=get_photo(name='buy'), chat_id=user.user_id, caption=lexicon['day_9'],
                                 reply_markup=keyboard_parts())
            elif (end + timedelta(days=1)) <= now:
                await bot.send_photo(photo=get_photo(name='buy'), chat_id=user.user_id, caption=lexicon['del_user'])
                await bot.send_message(chat_id=admin_id(),
                                       text=lexicon['for_admin_4'].format(user_phone=user.phone))
                await db_manager.delete_user(user_id=user.user_id)
                logging.debug(f'Kick user by id={user.user_id}')


async def check_link():
    d = {True: 'Договоры для Совершеннолетних', False: 'Договоры для Несовершеннолетних'}
    for key, item in d.items():
        links = await db_manager.get_links(status=key)
        logging.debug(f'Check_link')
        if links == []:
            await bot.send_message(chat_id=admin_id(), text=lexicon['new_links'].format(button=item), reply_markup=keyboard_friend.as_markup(resize_keyboard=True))
