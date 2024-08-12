import logging
from datetime import timedelta, date

from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery

from config import admin_id, db_config, provider_token
from database.requests import DatabaseManager
from lexicon import lexicon

logger = logging.getLogger(__name__)
router = Router()
router.message.filter(F.chat.type == 'private')
dsn = db_config()
db_manager = DatabaseManager(dsn=dsn)


@router.callback_query()
async def buy_subscribe(callback: CallbackQuery, bot: Bot):
    user = await db_manager.get_user(user_id=callback.from_user.id)
    if not user or user.subscription_status is False:
        await bot.send_invoice(
            chat_id=callback.from_user.id,
            need_name=True,
            need_email=True,
            need_phone_number=True,
            title='Подписка на канал',
            description='Подписка на платный закрытый канал',
            provider_token=provider_token(),
            currency='RUB',
            payload='buy_subscribe',
            start_parameter='text',
            prices=[
                LabeledPrice(label="rub", amount=300 * 100)
            ]
        )
    else:
        await callback.message.answer(lexicon['already_buy'])


@router.pre_checkout_query()
async def process_pre_check(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    logging.debug('pre_checkout_query', pre_checkout_query)


@router.message(F.successful_payment)
async def successful_payment_handler(message: Message, bot: Bot):
    start_date = date.today()
    end_date = start_date + timedelta(days=5)
    successful_payment = message.successful_payment
    user = await db_manager.get_user(user_id=message.from_user.id)
    await message.answer('🟢 Поздравляю! Подписка успешно подключена!')
    if user:
        await db_manager.update_user(user_id=message.from_user.id, user_data={'subscription_status': True,
                                                                              'subscription_start_date': start_date,
                                                                              'subscription_end_date': end_date})
    else:
        await db_manager.add_user(user_data={'user_id': message.from_user.id,
                                             'telegram_id': message.from_user.id,
                                             'username': successful_payment.order_info.name,
                                             'subscription_status': True,
                                             'subscription_start_date': start_date,
                                             'subscription_end_date': end_date})
        await message.answer(lexicon['link'].format(subscription_start_date=start_date.strftime('%d-%m-%y'),
                                                    subscription_end_date=end_date.strftime('%d-%m-%y')))
        await bot.send_message(chat_id=int(admin_id()),
                               text=lexicon['new_user'].format(user_full_name=successful_payment.order_info.name,
                                                               user_id=message.from_user.id,
                                                               user_email=successful_payment.order_info.email,
                                                               user_phone=successful_payment.order_info.phone_number))
