from aiogram.types import FSInputFile

from bot import bot
from config import db_config
from database.requests import DatabaseManager

dsn = db_config()
db_manager = DatabaseManager(dsn=dsn)


def get_photo(name):
    photo = FSInputFile(f'photo/{name}.png', filename=f'photo_{name}')
    return photo


async def send_link(status: bool, link: str):
    users = await db_manager.get_users()
    for user in users:
        if user.doc is None and user.request is True:
            await db_manager.update_user(user_id=user.user_id, user_data={'adult': status ,'doc': link, 'request': False})
            await bot.send_message(chat_id=user.user_id, text='Доступен договор, для удобства можете нажать /start')
            return True
    else:
        return False
