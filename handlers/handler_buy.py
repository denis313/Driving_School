import logging
import json
from collections import namedtuple
from datetime import timedelta, date

import yookassa
from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery, InputMediaPhoto
from typing_extensions import Optional

from config import admin_id, db_config, provider_token_yookassa
from database.requests import DatabaseManager
from keyboards import kb_buy, Pay, back, keyboard_buy
from lexicon import lexicon
from service import create_payment, get_photo
import keyboards

logger = logging.getLogger(__name__)
router = Router()
router.message.filter(F.chat.type == 'private')
dsn = db_config()
db_manager = DatabaseManager(dsn=dsn)




@router.callback_query(F.data.in_({'yookassa', 'yookassa_parts'}))
async def buy_subscribe(callback: CallbackQuery, bot: Bot):
    user = await db_manager.get_user(user_id=callback.from_user.id)
    prices = await db_manager.get_prices()
    if not user or user.status is False:
        mg = lexicon['parts']
        if callback.data == 'yookassa':
            cost = prices.price - user.total # total = 2500
            mg = 'После оплаты обязательно нажмите кнопку <b>Проверка оплаты✅</b>, чтобы убедиться, что оплата успешно прошла и обучение может начаться без задержек.'
        elif callback.data == 'yookassa_parts':
            cost = prices.prepayment  # cost = 5000
            if user.total == prices.prepayment:
                cost = prices.price - prices.prepayment
        url, id_prepayment = create_payment(amount=cost,
                                            description='Оплата обучения в Автошколе',
                                            chat_id=callback.from_user.id)
        await bot.edit_message_media(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            media=InputMediaPhoto(
                media=get_photo(name='buy'),
                caption=mg
            ),
            reply_markup=kb_buy(id_payment=id_prepayment, url=url, page='doc_sent')
        )
    else:
        await bot.edit_message_media(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            media=InputMediaPhoto(
                media=get_photo(name='buy'),
                caption=lexicon['already_buy']
            ),
            reply_markup=back(page='doc_sent')
        )


@router.callback_query(Pay.filter())
async def successful_payment_handler(callback: CallbackQuery, bot: Bot, callback_data: Pay):
    user = await db_manager.get_user(user_id=callback.from_user.id)
    payment = yookassa.Payment.find_one(callback_data.pay_id)
    prices = await db_manager.get_prices()
    if payment.status == 'succeeded':
        # if (payment.amount.value == str(prices.prepayment) or str(prices.price-prices.prepayment)) and user.total + int(payment.amount.value) != 250: # successfull = 5000 user_total + 5000 != 25000
        #     start_date = date.today()
        #     end_date = start_date + timedelta(days=30)
        #     total = user.total + int(payment.amount.value)
        #     print(1111)
        #     await db_manager.update_user(user_id=callback.from_user.id, user_data={'total': total,
        #                                                                           'end_date': end_date})
        #     await bot.edit_message_media(
        #         chat_id=callback.from_user.id,
        #         message_id=callback.message.message_id,
        #         media=InputMediaPhoto(
        #             media=get_photo(name='buy'),
        #             caption=f'🟢 Оплата прошла, вы уже выплатили {total}'
        #         ),
        #         reply_markup=keyboard_buy()
        #     )
        # else:
        #     print(2222)
        await db_manager.update_user(user_id=callback.from_user.id, user_data={'status': True,
                                                                              'total': prices.price,
                                                                              'end_date': None})
            # await bot.edit_message_media(
            #     chat_id=callback.from_user.id,
            #     message_id=callback.message.message_id,
            #     media=InputMediaPhoto(
            #         media=get_photo(name='buy'),
            #         caption='🟢 Поздравляю!\n'
            #                      'Обучение оплачено полностью❤️'
            #     ))
        if user.reg is False:
            for user_id in admin_id():
                await bot.send_message(chat_id=user_id,
                                   text=f'<b>🚨Обучение оплатил пользователь, {user.fio}.\n'
                                        f'Его номер телефона: {user.phone}🚨</b>')

            await db_manager.update_user(user_id=callback.from_user.id, user_data={'reg': True})
            await bot.edit_message_media(
                chat_id=callback.from_user.id,
                message_id=callback.message.message_id,
                media=InputMediaPhoto(
                    media=get_photo(name='buy'),
                    caption='🟢 Поздравляю! Оплата прошла!\n'
                                 'Ожидайте сообщение или звонок от администратора, '
                            'с вашими данными для обучения📩, Автошкола создала для вас Личный Кабинет '
                )
            )
