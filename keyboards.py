import base64
import sys
import uuid
from sys import prefix

from aiogram.types import InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


from lexicon import lexicon


# from service import bs64


# Класс для создания callback_data
class CallFactory(CallbackData, prefix='user', sep='-'):
    user_id: int
    mg: int


class CallbackFactory(CallbackData, prefix='doc', sep='-'):
    user_id: int
    mg: int


class IsIdPrepayment(CallbackData, prefix='id', sep=':'):
    payment_id: str

class Pay(CallbackData, prefix='pay', sep=':'):
    pay_id: str


def bs_64(payment):
    uuid_obj = uuid.UUID(payment)
    # Кодирование в Base64
    compressed_uuid = base64.urlsafe_b64encode(uuid_obj.bytes).rstrip(b'=').decode('utf-8')
    return compressed_uuid


def de_bs64(compressed_uuid):
    # Декодируем из Base64
    uuid_bytes = base64.urlsafe_b64decode(compressed_uuid)
    # Преобразуем байты обратно в объект UUID
    decoded_uuid = uuid.UUID(bytes=uuid_bytes)
    return decoded_uuid


def keyboard_back(call):
    buttons = [(InlineKeyboardButton(text='Назад 🔙', callback_data=call)),
               (InlineKeyboardButton(text='Тех. Поддержка🚨', callback_data='help'))]

    return buttons


def keyboard_page_2():
    page_2 = InlineKeyboardBuilder()
    page_2.row(*[(InlineKeyboardButton(text='Полетели ✈', callback_data='page_2')),
                 (InlineKeyboardButton(text='Тех. Поддержка🚨', callback_data='help'))], width=1)

    return page_2.as_markup()


def keyboard_page_3():
    page_3 = InlineKeyboardBuilder()
    page_3.row(*[(InlineKeyboardButton(text='Как нас найти 🔜', callback_data='page_3'))], width=1)

    return page_3.row(*next_photo(mg='Фото Автодрома🚘', cal='next_1')).row(*next_photo(mg='Тех. Поддержка🚨', cal='help')).as_markup()


def keyboard_page_4(mg_text: str, mg_cal):
    page_4 = InlineKeyboardBuilder()
    page_4.row(*[(InlineKeyboardButton(text='Запись на обучение 🚀', callback_data='page_4'))], width=1)

    return page_4.row(*next_photo(mg=mg_text, cal=mg_cal)).row(*keyboard_back(call='page_2')).as_markup()


def keyboard_page_5():
    page_5 = InlineKeyboardBuilder()
    page_5.row(*[(InlineKeyboardButton(text='1. Подписать Договор📑', callback_data='page_5'))], width=1)

    return page_5.row(*keyboard_back(call='page_3')).as_markup()


def keyboard_page_6():
    page_6 = InlineKeyboardBuilder()
    page_6.row(*[(InlineKeyboardButton(text='✅ Согласен на обработку данных', callback_data='page_6'))], width=1)

    return page_6.row(*keyboard_back(call='page_4')).as_markup()



def keyboard_page_7():
    page_7 = InlineKeyboardBuilder()
    page_7.row(*[(InlineKeyboardButton(text='✅ Да, мне уже 18', callback_data='adult')),
                 (InlineKeyboardButton(text='❌ Нет, мне от 16 до 18', callback_data='no_adult'))], width=2)

    return page_7.row(*keyboard_back(call='page_5')).as_markup()


def keyboard_page_8(page: str, name: str):
    page_8 = InlineKeyboardBuilder()
    page_8.row(*[(InlineKeyboardButton(text=name, callback_data=page))], width=1)

    return page_8.row(*keyboard_back(call='page_6')).as_markup()


def keyboard_page_9(page):
    yes = InlineKeyboardBuilder()
    yes.row(*[(InlineKeyboardButton(text='Договор отправил ✔️', callback_data='page_9'))])

    return yes.row(*keyboard_back(call=page)).as_markup()


def keyboard_prepayment(url:str, id_payment, page):
    kb = InlineKeyboardBuilder()
    kb.row(*[InlineKeyboardButton(text='Предоплата 💳', url=url),
             InlineKeyboardButton(text='Проверка оплаты ✅',
                                  callback_data=IsIdPrepayment(payment_id=id_payment).pack())],
           width=1)
    return kb.row(*keyboard_back(call=page)).as_markup()


def keyboard_buy():
    buy = InlineKeyboardBuilder()
    buy.row(
        *[(InlineKeyboardButton(text='Единоразовая оплата', callback_data='yookassa')),
          (InlineKeyboardButton(text='Оплата частями', callback_data='parts'))],
        width=1)

    return buy.row(*keyboard_back(call='page_8')).as_markup()


# def keyboard_buy():
#     buy = InlineKeyboardBuilder()
#     buy.row(
#         *[(InlineKeyboardButton(text='Единоразовая оплата', callback_data='yookassa')),],
#         width=1)
#
#     return buy.row(*keyboard_back(call='page_8')).as_markup()


def keyboard_parts():
    buy = InlineKeyboardBuilder()
    buy.row(
        *[(InlineKeyboardButton(text='Обучение в рассрочку💰', callback_data='yookassa_parts'))],
        width=1)

    return buy.row(*keyboard_back(call='buy_all')).as_markup()


def allow_payment(user_id: int, mg_id: int):
    payment = InlineKeyboardBuilder()
    payment.row(
        *[(InlineKeyboardButton(text='Предоставить оплату 💳',
                                callback_data=CallbackFactory(user_id=user_id, mg=mg_id).pack()))],
        width=1)

    return payment.as_markup()


def back(page: str):
    back_kb = InlineKeyboardBuilder()
    back_kb.row(*keyboard_back(call=page))
    return back_kb.as_markup()


keyboard_friend = (ReplyKeyboardBuilder())
(keyboard_friend.row(*[KeyboardButton(text=bt) for bt in lexicon["button"]], width=2))


def next_photo(mg: str, cal):
    button = [(InlineKeyboardButton(text=mg,callback_data=cal))]
    return button


contact_keyboard = ReplyKeyboardBuilder().add(KeyboardButton(text="📱 Отправить Телефон", request_contact=True))


def admin_kb():
    kb = InlineKeyboardBuilder()
    kb.row(*[InlineKeyboardButton(text='Остаток ссылок 📲', callback_data='rest_links'),
             InlineKeyboardButton(text='Отправленные ссылки 📲', callback_data='sent_links')], width=1)
    return kb.as_markup()


def kb_buy(url:str, id_payment, page):
    kb = InlineKeyboardBuilder()
    kb.row(*[InlineKeyboardButton(text='Оплата 💳', url=url),
             InlineKeyboardButton(text='Проверка оплаты ✅',
                                  callback_data=Pay(pay_id=id_payment).pack())],
           width=1)
    return kb.row(*keyboard_back(call=page)).as_markup()
