import logging
import json
from datetime import timedelta, date

import yookassa
from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery, InputMediaPhoto

from config import admin_id, db_config, provider_token_yookassa
from database.requests import DatabaseManager
from keyboards import kb_buy, Pay, back, keyboard_buy
from lexicon import lexicon
from service import create_payment, get_photo

logger = logging.getLogger(__name__)
router = Router()
router.message.filter(F.chat.type == 'private')
dsn = db_config()
db_manager = DatabaseManager(dsn=dsn)




@router.callback_query(F.data.in_({'yookassa', 'yookassa_parts'}))
async def buy_subscribe(callback: CallbackQuery, bot: Bot):
    user = await db_manager.get_user(user_id=callback.from_user.id)
    if not user or user.status is False:
        mg = ('Платеж за обучение будет производиться один раз в месяц.'
              ' Каждый месяц вы будете получать сообщение с требованием произвести очередной платеж. '
              'После каждого платежа обязательно нажмите кнопку "Проверка оплаты ✅", чтобы убедиться, '
              'что оплата успешно прошла и обучение может продолжаться без задержек.')
        if callback.data == 'yookassa':
            cost = 25000 - user.total # total = 2500
            mg = ('Для оформления обучения предусмотрена единоразовая оплата. '
                  'Пожалуйста, внесите полную сумму для завершения процесса. '
                  'После оплаты обязательно нажмите кнопку "Проверка оплаты✅", '
                  'чтобы убедиться, что оплата успешно прошла и обучение может начаться без задержек.')
        elif callback.data == 'yookassa_parts':
            cost = 5000  # cost = 5000
            if user.total == 50:
                cost = 4950
        url, id_prepayment = create_payment(amount=cost,
                                            description='Оплата обучения в Автошколе',
                                            chat_id=callback.from_user.id)
        await bot.edit_message_media(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            media=InputMediaPhoto(
                media=get_photo(name=10),
                caption=mg
            ),
            reply_markup=kb_buy(id_payment=id_prepayment, url=url, page='page_9')
        )
    else:
        await bot.edit_message_media(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            media=InputMediaPhoto(
                media=get_photo(name=10),
                caption=lexicon['already_buy']
            ),
            reply_markup=back(page='page_9')
        )


@router.callback_query(Pay.filter())
async def successful_payment_handler(callback: CallbackQuery, bot: Bot, callback_data: Pay):
    user = await db_manager.get_user(user_id=callback.from_user.id)
    payment = yookassa.Payment.find_one(callback_data.pay_id)
    if payment.status == 'succeeded':
        if (payment.amount.value == '5000' or '4950') and user.total + int(payment.amount.value) != 25000: # successfull = 5000 user_total + 5000 != 25000
            start_date = date.today()
            end_date = start_date + timedelta(days=30)
            total = user.total + int(payment.amount.value)
            await db_manager.update_user(user_id=callback.from_user.id, user_data={'total': total,
                                                                                  'end_date': end_date})
            await bot.edit_message_media(
                chat_id=callback.from_user.id,
                message_id=callback.message.message_id,
                media=InputMediaPhoto(
                    media=get_photo(name=10),
                    caption=f'🟢 Оплата прошла, вы уже выплатили {total}'
                ),
                reply_markup=keyboard_buy()
            )
        else:
            await db_manager.update_user(user_id=callback.from_user.id, user_data={'status': True,
                                                                                  'total': 25000,
                                                                                  'end_date': None})
            await bot.edit_message_media(
                chat_id=callback.from_user.id,
                message_id=callback.message.message_id,
                media=InputMediaPhoto(
                    media=get_photo(name=10),
                    caption='🟢 Поздравляю!\n'
                                 'Обучение оплачено полностью❤️'
                ))
        if user.reg is False:
            await bot.send_message(chat_id=admin_id(),
                                   text=f'Зарегистрировался новый пользователь, phone={user.phone}')
            await db_manager.update_user(user_id=callback.from_user.id, user_data={'reg': True})
            await bot.edit_message_media(
                chat_id=callback.from_user.id,
                message_id=callback.message.message_id,
                media=InputMediaPhoto(
                    media=get_photo(name=10),
                    caption='🟢 Поздравляю! Оплата прошла!\n'
                                 'Ожидайте сообщение на почту и звонок от администратора, '
                            'с вашими данными для обучения📩, Автошкола создала для вас Личный Кабинет '
                )
            )
