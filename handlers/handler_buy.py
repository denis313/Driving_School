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
from handlers.for_admin import second_payment
from keyboards import kb_buy, Pay, back, keyboard_buy, keyboard_link, exactly_kb, exactly_kb, exactly_shares_kb
from lexicon import lexicon
from service import create_payment, get_photo
import keyboards

logger = logging.getLogger(__name__)
router = Router()
router.message.filter(F.chat.type == 'private')
dsn = db_config()
db_manager = DatabaseManager(dsn=dsn)




@router.callback_query(F.data.in_({'individually', 'now_25', 'now_50', 'now_75', 'shares_100', 'now_100'}))
async def buy_subscribe(callback: CallbackQuery, bot: Bot):
    user = await db_manager.get_user(user_id=callback.from_user.id)

    if not user:
        await bot.send_message(callback.from_user.id, "Ошибка: пользователь не найден.")
        return

    # Если выбрано 'individually', сразу отправляем сообщение и выходим
    if callback.data == 'individually' and user.status != True:
        await bot.edit_message_media(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            media=InputMediaPhoto(
                media=get_photo(name='buy'),
                caption=lexicon['exactly_ind']
            ),
            reply_markup=exactly_kb()  # Убираем клавиатуру
        )
        return

    percent = int(callback.data.split('_')[1]) if '_' in callback.data else 100

    link_obj = await db_manager.get_tblink(percent=percent)
    status = False
    id_link = None

    if link_obj:
        link, id_link = link_obj.link, link_obj.id_link
    else:
        link = '<b>Ожидайте договор "Долями"</b>'
        await db_manager.update_user(user_id=callback.from_user.id, user_data={'tb_link': False})

    if not user.status:
        mg = lexicon['parts']
        payment = 0
        cost = 0  # Инициализация переменной

        if callback.data == 'now_100':
            cost = user.price - user.total
            mg = lexicon['base_pay']
            status = True
        elif callback.data == 'shares_100':
            cost = user.price - user.prepayment
            await bot.edit_message_media(
                chat_id=callback.from_user.id,
                message_id=callback.message.message_id,
                media=InputMediaPhoto(
                    media=get_photo(name='buy'),
                    caption=lexicon['exactly_ind']
                ),
                reply_markup=exactly_shares_kb()
            )
            return
        elif callback.data == 'now_75':
            cost = ((user.price - user.total) * 75) / 100
            mg += lexicon['payment_installments'].format(link=link)
            payment = user.price - user.prepayment - cost
        elif callback.data == 'now_50':
            cost = ((user.price - user.prepayment) * 50) / 100
            mg += lexicon['payment_installments'].format(link=link)
            payment = user.price - user.prepayment - cost
        elif callback.data == 'now_25':
            cost = ((user.price - user.prepayment) * 25) / 100
            mg += lexicon['payment_installments'].format(link=link)
            payment = user.price - user.prepayment - cost

        url, id_prepayment = create_payment(
            amount=int(cost),
            description='Оплата обучения в Автошколе',
            chat_id=callback.from_user.id
        )

        kb = kb_buy(
                id_payment=id_prepayment,
                url=url,
                page='doc_sent',
                second_payment=str(payment),
                status=status,
                id_link=str(id_link) if id_link is not None else ""
            )

        await bot.edit_message_media(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            media=InputMediaPhoto(
                media=get_photo(name='buy'),
                caption=mg
            ),
            reply_markup=kb
        )
    else:
        if user.link:
            kb = keyboard_link(url_link=user.link)
        else:
            kb = back(page='doc_sent')
        await bot.edit_message_media(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            media=InputMediaPhoto(
                media=get_photo(name='buy'),
                caption=lexicon['already_buy']
            ),
            reply_markup=kb
        )


@router.callback_query(Pay.filter())
async def successful_payment_handler(callback: CallbackQuery, bot: Bot, callback_data: Pay):
    user = await db_manager.get_user(user_id=callback.from_user.id)
    payment = yookassa.Payment.find_one(callback_data.pay_id)
    if payment.status == 'succeeded':
        kb = None
        if callback_data.status == True:
            text = lexicon['pay_T']
            data = {'status': True, 'total': user.price, 'end_date': None, 'tb_link': True}
            kb = None
        else:
            text = lexicon['pay_F']
            data = {'status': True, 'total': user.price, 'end_date': None}
            if callback_data.id_link:
                link = await db_manager.get_tblink_by_linkid(id_link=int(callback_data.id_link))
                kb = keyboard_link(url_link=link.link)
                data = {'status': True, 'total': user.price, 'end_date': None, 'tb_link': True, 'link': link.link}
                await db_manager.delete_tblink(link_id=int(callback_data.id_link))
        if user.reg is False:
            await bot.send_message(chat_id=admin_id(),
                               text=f'<b>🚨Обучение оплатил пользователь, {user.fio}.\n'
                                    f'Его номер телефона: {user.phone}🚨</b>\n'
                                    f'Пользователь должен оплатить {callback_data.second_pay}')

        await bot.edit_message_media(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            media=InputMediaPhoto(
                media=get_photo(name='buy'),
                caption=text
            ),
            reply_markup=kb
        )
        await db_manager.update_user(user_id=callback.from_user.id, user_data=data)
        # await db_manager.update_user(user_id=user.user_id, user_data=data)


@router.callback_query(F.data == 'exactly')
async def exactly(callback: CallbackQuery, bot: Bot):
    await bot.edit_message_media(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(
            media=get_photo(name='buy'),
            caption=lexicon['individually']
        )
    )
    user = await db_manager.get_user(user_id=callback.from_user.id)
    await bot.send_message(chat_id=admin_id(), text=f'Пользователь {user.phone}, хочет индивидуальное предложение\n'
                                                    f'Свяжитесь с ним')
    await db_manager.update_user(user_id=callback.from_user.id, user_data={'status': True})



@router.callback_query(F.data == 'shares')
async def exactly(callback: CallbackQuery, bot: Bot):
    link_obj = await db_manager.get_tblink(percent=100)

    if link_obj:
        link, id_link = link_obj.link, link_obj.id_link
        await db_manager.delete_link(link_id=id_link)
    else:
        link = '<b>Ожидайте договор "Долями"</b>'
        await db_manager.update_user(user_id=callback.from_user.id, user_data={'tb_link': False})
    await bot.edit_message_media(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(
            media=get_photo(name='buy'),
            caption=lexicon['shares_100'] + lexicon['payment_installments'].format(link=link)  # Или нужное сообщение
        )
    )

    await db_manager.update_user(user_id=callback.from_user.id,
                                 user_data={'link': None if link == '<b>Ссылка на сервис пока не готова.\n'
                                                                    'Ожидайте договор "Долями"</b>' else link,
                                            'status': True})
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
        # await db_manager.update_user(user_id=callback.from_user.id, user_data={'status': True,
        #                                                                       'total': prices.price,
        #                                                                       'end_date': None})
        # await bot.edit_message_media(
        #     chat_id=callback.from_user.id,
        #     message_id=callback.message.message_id,
        #     media=InputMediaPhoto(
        #         media=get_photo(name='buy'),
        #         caption='🟢 Поздравляю!\n'
        #                      'Обучение оплачено полностью❤️'
        #     ))