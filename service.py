import base64
import re
import uuid
from gc import callbacks

from aiogram.types import Message, CallbackQuery

from aiogram.types import FSInputFile
from aiogram.filters import BaseFilter
from bot import bot
from config import db_config
from database.requests import DatabaseManager
from yookassa import Configuration, Payment


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

class IsPhone(BaseFilter):
    async def __call__(self, message: Message):
        try:
            if message.contact.phone_number:
                return True
        except AttributeError:
            match = re.fullmatch(r'\+7\d{3}\d{7}', message.text.strip())
            return bool(match)


class IsPage(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        try:
            return callback.data == 'page_8'
        except AttributeError:
            return False



def create_payment(amount: int, description: str, chat_id: int):
    Configuration.account_id = '463028'
    Configuration.secret_key = 'test_8uk2ZCfR3aMZYtZechnFWVuCSdhWjepP3r4NUrya1dU'
    payment = Payment.create({
        "amount": {
            "value": f"{amount}.00",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/test_driving_school_bot"
        },
        "capture": True,
        "metadata": {
            'chat_id': chat_id
        },
        "description": description
    }, uuid.uuid4())
    return payment.confirmation.confirmation_url, payment.id



