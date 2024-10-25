import re
import uuid

from aiogram.types import Message, CallbackQuery

from aiogram.types import FSInputFile
from aiogram.filters import BaseFilter
from bot import bot
from config import db_config, yookassa
from database.requests import DatabaseManager
from yookassa import Configuration, Payment

from keyboards import keyboard_doc, back
from lexicon import lexicon

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
            match = re.fullmatch(r'\+7\d{3}\d{7}', message.text.strip()[-1])
            return bool(match)
        except AttributeError:
            return False



class IsPage(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        try:
            return callback.data == 'page_8'
        except AttributeError:
            return False



def filter_url(url):
    pattern = r"^https:\/\/.+"
    return bool(re.match(pattern, url.strip()))


def create_payment(amount: int, description: str, chat_id: int):
    account_id, secret_key = yookassa()
    Configuration.account_id = account_id
    Configuration.secret_key = secret_key
    payment = Payment.create({
        "amount": {
            "value": f"{amount}.00",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/Avtokosmos17_bot"
        },
        "payment_method_data": {
            "type": "sbp"
        },
        "capture": True,
        "metadata": {
            'chat_id': chat_id
        },
        "description": description
    }, uuid.uuid4())
    print(payment)
    return payment.confirmation.confirmation_url, payment.id


async def get_document(user_id: int):
    age = {True: 'adult', False: 'no_adult'}
    user = await db_manager.get_user(user_id=user_id)
    link = await db_manager.get_link(status=user.adult)  # Получаем ссылку на основе статуса возраста
    photo = get_photo(name='doc')
    text = lexicon['doc']
    kb = keyboard_doc(url_doc=user.doc, page='about_us')
    if user.doc is None:
        if link:
            await db_manager.update_user(user_id=user_id, user_data={'doc': str(link.link)})
            await db_manager.delete_link(link_id=link.id_link)
        else:
            text = lexicon['expectation']
            kb = back(page='about_us')
            await db_manager.update_user(user_id=user_id, user_data={'request': True})
    return text, kb, photo
