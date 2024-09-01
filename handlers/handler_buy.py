import logging
import json
from datetime import timedelta, date

from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery

from config import admin_id, db_config, provider_token_yookassa
from database.requests import DatabaseManager
from lexicon import lexicon

logger = logging.getLogger(__name__)
router = Router()
router.message.filter(F.chat.type == 'private')
dsn = db_config()
db_manager = DatabaseManager(dsn=dsn)


@router.callback_query(F.data.in_({'yookassa', 'yookassa_parts'}))
async def buy_subscribe(callback: CallbackQuery, bot: Bot):
    user = await db_manager.get_user(user_id=callback.from_user.id)
    if not user or user.status is False:
        if callback.data == 'yookassa':
            cost = 450 - user.total # total = 25000
        elif callback.data == 'yookassa_parts':
            cost = 90 # cost = 5000
        await bot.send_invoice(
            chat_id=callback.from_user.id,
            need_name=True,
            need_email=True,
            need_phone_number=True,
            send_email_to_provider=True,
            send_phone_number_to_provider=True,
            title='Оплата обучения',
            description='Оплата обучения в автошколе "Космос"',
            provider_token=provider_token_yookassa(),
            currency='RUB',
            payload=str(cost),  # Указываем сумму в копейках в payload
            start_parameter='text',
            provider_data=json.dumps({
                "receipt": {
                    "items": [
                        {
                            "description": "Оплата обучения в автошколе 'Космос'",
                            "quantity": "1",
                            "amount": {
                                "value": f"{cost}",  # Сумма в рублях с двумя знаками после запятой
                                "currency": "RUB"
                            },
                            "vat_code": 1
                        }
                    ]
                }
            }),
            prices=[
                LabeledPrice(label="rub", amount=cost*100)
            ]
        )
    else:
        await callback.message.answer(lexicon['already_buy'])


@router.pre_checkout_query()
async def process_pre_check(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.successful_payment)
async def successful_payment_handler(message: Message, bot: Bot):
    user = await db_manager.get_user(user_id=message.from_user.id)
    successful_payment = message.successful_payment
    if message.successful_payment.invoice_payload == '90' and user.total + 90 != 450: # successfull = 5000 user_total + 5000 != 25000
        start_date = date.today()
        end_date = start_date + timedelta(days=2)
        total = user.total + int(message.successful_payment.invoice_payload)
        await db_manager.update_user(user_id=message.from_user.id, user_data={'total': total,
                                                                              'start_date': start_date,
                                                                              'end_date': end_date})
        await message.answer(f'🟢 Оплата прошла, вы уже выплатили {total}')
    else:
        await db_manager.update_user(user_id=message.from_user.id, user_data={'status': True,
                                                                              'total': 25000,
                                                                              'start_date': None,
                                                                              'end_date': None})
        await message.answer('🟢 Поздравляю!\n'
                             'Обучение оплачено полностью❤️')
    if user.reg is False:
        await bot.send_message(chat_id=admin_id(),
                           text=lexicon['for_admin_3'].format(user_name=successful_payment.order_info.name,
                                                              user_id=message.from_user.id,
                                                              user_email=successful_payment.order_info.email,
                                                              user_phone=successful_payment.order_info.phone_number))
        await db_manager.update_user(user_id=message.from_user.id, user_data={'reg': True,
                                                                              'name': successful_payment.order_info.name,
                                                                              'email': successful_payment.order_info.email,
                                                                              'phone': successful_payment.order_info.phone_number})
        await message.answer('🟢 Поздравляю! Оплата прошла!\n'
                             'Ожидайте сообщение на почту, с вашими данными для обучения📩')
