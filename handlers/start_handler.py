import logging

import yookassa
from yookassa.configuration import ConfigurationError
from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, StatesGroup, State
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, FSInputFile, ReplyKeyboardRemove
from sqlalchemy.testing.suite.test_reflection import users

from bot import bot
from config import db_config, admin_id
from database.requests import DatabaseManager
from keyboards import keyboard_parts, allow_payment, \
    back, keyboard_buy, \
    keyboard_page_8, contact_keyboard, admin_kb, keyboard_prepayment, \
    IsIdPrepayment, sign_contract, keyboard_start, age, keyboard_doc, keyboard_back, next_stap
from lexicon import lexicon
from service import get_photo, IsPhone, create_payment, IsPage, get_document

router = Router()
router.message.filter(F.chat.type == 'private')
dsn = db_config()
db_manager = DatabaseManager(dsn=dsn)


@router.message(CommandStart(), StateFilter(default_state))
async def page_one(message: Message):
    await db_manager.create_tables()
    user = await db_manager.get_user(user_id=message.from_user.id)
    if user:
        kb = 'about_us'
    else:
        kb = 'form'
    await bot.send_photo(chat_id=message.from_user.id, photo=get_photo(name=1), caption=lexicon['start'], reply_markup=keyboard_start(page=kb))
    if str(message.from_user.id) == admin_id():
        await message.answer("Вы администратор +", reply_markup=admin_kb())

class FioPhone(StatesGroup):
    fio_phone = State()
    mg_id = State()


@router.callback_query(F.data.in_({'form', 'redact'}))
async def form(callback: CallbackQuery, state: FSMContext):
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(
            media=get_photo(name='about_us'),
            caption=lexicon['form']
        ),
        reply_markup=None)
    await state.set_state(FioPhone.fio_phone)
    await state.update_data(mg_id=callback.message.message_id)


@router.message(StateFilter(FioPhone.fio_phone), F.text.split().len() == 4)
async def fio_form(message: Message, state: FSMContext):
    await state.update_data(fio_phone=message.text)
    data = await state.get_data()
    user = data['fio_phone'].split()
    await state.clear()
    fio, phone = ' '.join(user[:3]), user[-1]
    users = await db_manager.get_user(user_id=message.from_user.id)
    if users:
        await db_manager.update_user(user_id=message.from_user.id, user_data={'fio': fio, 'phone': phone})
    else:
        await db_manager.add_user(user_data={'user_id': message.from_user.id, 'fio': fio, 'phone': phone})
    await message.delete()
    await bot.send_message(chat_id=admin_id(), text=lexicon['user_form'].format(fio=fio, phone=phone))
    await bot.edit_message_media(
        chat_id=message.chat.id,
        message_id=data['mg_id'],
        media=InputMediaPhoto(
            media=get_photo(name='about_us'),
            caption=lexicon['form']
        ),
        reply_markup=sign_contract())


@router.message(StateFilter(FioPhone.fio_phone))
async def not_fio_form(message: Message, state: FSMContext):
    data = await state.get_data()
    await bot.edit_message_media(
        chat_id=message.chat.id,
        message_id=data['mg_id'],
        media=InputMediaPhoto(
            media=get_photo(name='about_us'),
            caption=lexicon['no_form']
        ),
        reply_markup=None)


@router.callback_query(F.data == 'about_us')
async def about_us(callback: CallbackQuery):
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(
            media=get_photo(name='building'),
            caption=lexicon['about_us']
        ),
        reply_markup=next_stap())


@router.callback_query(F.data == 'contract')
async def handle_next_photo(callback: CallbackQuery):
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(
            media=get_photo(name='age'),
            caption=lexicon['contract']
        ),
        reply_markup=age())


@router.callback_query(F.data.in_({'adult', 'no_adult'}))
async def page_seven(callback: CallbackQuery):
    user = await db_manager.get_user(user_id=callback.from_user.id)
    page = 'contract'
    text = lexicon['prepayment']
    photo = get_photo(name='prepayment')
    if user.total < 50:
        url, id_payment = create_payment(amount=50,
                                         description="Предоплата для получения договора",
                                         chat_id=callback.from_user.id)
        kb = keyboard_prepayment(url=url, id_payment=id_payment, page=page)
        if callback.data == 'adult':
            adult = True
            doc = FSInputFile('handlers/document.pdf', filename='Образец Договора.pdf')
        else:
            adult = False
            doc = FSInputFile('handlers/document_2.pdf', filename='Образец Договора.pdf')
        await db_manager.update_user(user_id=callback.from_user.id, user_data={'adult': adult})
        await bot.send_document(chat_id=callback.message.chat.id,
                                document=doc)
    else:
        text, kb, photo = await get_document(user_id=user.user_id)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(
            media=photo,
            caption=text
        ),
        reply_markup=kb)


@router.callback_query(IsIdPrepayment.filter())
async def page_eight(callback: CallbackQuery, callback_data: IsIdPrepayment):
    try:
        payment = yookassa.Payment.find_one(callback_data.payment_id)
        if payment.status == 'succeeded':
            await db_manager.update_user(user_id=callback.from_user.id, user_data={'total': 50})
            text, kb, photo = await get_document(user_id=callback.from_user.id)
        else:
            text = lexicon['prepayment_failed']
            kb = back(page='contract')
            photo = get_photo(name='failed')
    except ConfigurationError:
        text = lexicon['not_pay']
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(
            media=photo,
            caption=text
        ),
        reply_markup=kb)


@router.callback_query(F.data == 'doc_sent')
async def handle_next_photo(callback: CallbackQuery):
    user = await db_manager.get_user(user_id=callback.from_user.id)
    if user.buy is False:
        kb = back(page='about_us')
        mg = lexicon['wait']
        photo = get_photo(name='wait')
        await bot.send_message(chat_id=admin_id(), text=lexicon['for_admin_2'],
                               reply_markup=allow_payment(user_id=callback.from_user.id,
                                                          mg_id=callback.message.message_id))
    else:
        kb = keyboard_buy()
        mg = lexicon['buy']
        photo = get_photo(name='buy')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(
            media=photo,
            caption=mg
        ),
        reply_markup=kb)


@router.callback_query(F.data == 'help')
async def help_handler(callback: CallbackQuery):
    await bot.send_message(chat_id=callback.from_user.id, text='Если у вас возникли проблемы, вы можете позвонить по номеру ☎️Тел +79232656553\n'
                                       'Вам постараются помочь в вашем вопросе')


# @router.callback_query(F.data == 'next_2')
# async def handle_next_photo(callback: CallbackQuery):
#     try:
#         await bot.edit_message_media(
#             chat_id=callback.message.chat.id,
#             message_id=callback.message.message_id,
#             media=InputMediaPhoto(
#                 media=get_photo(name='next_3'),
#                 caption=lexicon['three']
#             ),
#             reply_markup=keyboard_page_4(mg_text='Мы на карте🗺', mg_cal='next_3'))
#     except TelegramBadRequest:
#         pass


# @router.callback_query(F.data == 'next_3')
# async def handle_next_photo(callback: CallbackQuery):
#     try:
#         await bot.edit_message_media(
#             chat_id=callback.message.chat.id,
#             message_id=callback.message.message_id,
#             media=InputMediaPhoto(
#                 media=get_photo(name=3),
#                 caption=lexicon['three']
#             ),
#             reply_markup=keyboard_page_4(mg_text='Наша Автошкола🏫', mg_cal='next_3'))
#     except TelegramBadRequest:
#         pass


# @router.callback_query(F.data == 'page_4')
# async def page_four(callback: CallbackQuery):
#     await bot.edit_message_media(
#         chat_id=callback.message.chat.id,
#         message_id=callback.message.message_id,
#         media=InputMediaPhoto(
#             media=get_photo(name=4),
#             caption=lexicon['four']
#         ),
#         reply_markup=keyboard_page_5())
#
#
# @router.callback_query(F.data == 'page_5')
# async def page_fife(callback: CallbackQuery):
#     await bot.edit_message_media(
#         chat_id=callback.message.chat.id,
#         message_id=callback.message.message_id,
#         media=InputMediaPhoto(
#             media=get_photo(name=5),
#             caption=lexicon['fife']
#         ),
#         reply_markup=keyboard_page_6())
#
#
#
# @router.callback_query(F.data == 'page_6')
# async def page_six(callback: CallbackQuery):
#     await bot.edit_message_media(
#         chat_id=callback.message.chat.id,
#         message_id=callback.message.message_id,
#         media=InputMediaPhoto(
#             media=get_photo(name=6),
#             caption=lexicon['six']
#         ),
#         reply_markup=keyboard_page_7())
#     await db_manager.add_user(user_data={'user_id': callback.from_user.id})
#     user = await db_manager.get_user(user_id=callback.from_user.id)
#     if user.phone is None or user.fio is None:
#         await callback.message.answer("Нажмите на кнопку ниже, чтобы отправить контакт и ФИО",
#                                       reply_markup=contact_keyboard.as_markup(resize_keyboard=True))
#
#

#
#
# @router.callback_query(F.data == 'prepayment')
# async def prepayment(callback: CallbackQuery):
#     url, id_payment = create_payment(amount=50,
#                                      description="Предоплата для получения договора",
#                                      chat_id=callback.from_user.id)
#     await bot.edit_message_media(
#         chat_id=callback.message.chat.id,
#         message_id=callback.message.message_id,
#         media=InputMediaPhoto(
#             media=get_photo(name=13),
#             caption=lexicon['prepayment']
#         ),
#         reply_markup=keyboard_prepayment(url=url, id_payment=id_payment, page='page_6'))
#
#
# @router.callback_query(IsIdPrepayment.filter())
# async def page_eight(callback: CallbackQuery, callback_data: IsIdPrepayment):
#     user_id = callback.from_user.id
#     chat_id = callback.message.chat.id
#     message_id = callback.message.message_id
#     user = await db_manager.get_user(user_id=user_id)  # Получаем данные пользователя
#     page = 'adult' if user.adult else 'no_adult'  # Определяем страницу для клавиатуры
#     payment = yookassa.Payment.find_one(callback_data.payment_id)
#     if payment.status == 'succeeded':
#         kb = keyboard_page_9(page=page, url_doc=user.doc)
#         link = await db_manager.get_link(status=user.adult)  # Получаем ссылку на основе статуса возраста
#         mg = lexicon['waiting']  # Инициализируем переменную mg на случай, если ни одно из условий не выполнится
#         if user.doc:
#             mg = lexicon['eight'].format(url=user.doc)  # Если документ уже существует
#         elif link:
#             await db_manager.update_user(user_id=user_id, user_data={
#                 'doc': str(link.link), 'total': 50})  # Обновляем данные пользователя и удаляем использованную ссылку
#             await db_manager.delete_link(link_id=link.id_link)
#             mg = lexicon['eight'].format(url=link.link)
#         else:
#             kb = back(page='page_5')  # Если ссылка не найдена, используем альтернативный текст
#             await db_manager.update_user(user_id=user_id, user_data={'request': True, 'total': 50})
#         photo = get_photo(name=8)
#         await bot.send_message(chat_id=admin_id(),
#                                text=f'Пользователь, {user.fio}, его номер: {user.phone}. Оплатил предоплату')
#     else:
#         url, id_payment = create_payment(amount=50,
#                                          description="Предоплата для получения договора",
#                                          chat_id=callback.from_user.id)
#         mg = 'Оплата не прошла'
#         kb = keyboard_prepayment(url=url, id_payment=id_payment, page=page)
#         photo = get_photo(name=15)
#     await bot.edit_message_media(
#         chat_id=chat_id,
#         message_id=message_id,
#         media=InputMediaPhoto(
#             media=photo,
#             caption=mg
#         ),
#         reply_markup=kb
#     )
#
#
# @router.callback_query(F.data == 'page_8')
# async def page_eight_plus(callback: CallbackQuery):
#     user_id = callback.from_user.id
#     chat_id = callback.message.chat.id
#     message_id = callback.message.message_id
#     user = await db_manager.get_user(user_id=user_id)  # Получаем данные пользователя
#     page = 'adult' if user.adult else 'no_adult'  # Определяем страницу для клавиатуры
#     kb = keyboard_page_9(page=page, url_doc=user.doc)
#     link = await db_manager.get_link(status=user.adult)  # Получаем ссылку на основе статуса возраста
#     mg = lexicon['waiting']  # Инициализируем переменную mg на случай, если ни одно из условий не выполнится
#     if user.doc:
#         mg = lexicon['eight'].format(url=user.doc)  # Если документ уже существует
#     elif link:
#         await db_manager.update_user(user_id=user_id, user_data={
#             'doc': str(link.link)})  # Обновляем данные пользователя и удаляем использованную ссылку
#         await db_manager.delete_link(link_id=link.id_link)
#         mg = lexicon['eight'].format(url=link.link)
#     else:
#         kb = back(page='page_5')  # Если ссылка не найдена, используем альтернативный текст
#         await db_manager.update_user(user_id=user_id, user_data={'request': True})
#     await bot.edit_message_media(
#         chat_id=chat_id,
#         message_id=message_id,
#         media=InputMediaPhoto(
#             media=get_photo(name=8),
#             caption=mg
#         ),
#         reply_markup=kb
#     )
#
#
# @router.callback_query(F.data == 'page_9')
# async def page_nine(callback: CallbackQuery):
#     user = await db_manager.get_user(user_id=callback.from_user.id)
#     if user.buy is False:
#         kb = back(page='page_8')
#         mg = lexicon['nine']
#         photo = get_photo(name=9)
#         await bot.send_message(chat_id=admin_id(), text=lexicon['for_admin_2'],
#                                reply_markup=allow_payment(user_id=callback.from_user.id,
#                                                           mg_id=callback.message.message_id))
#     else:
#         kb = keyboard_buy()
#         mg = lexicon['buy']
#         photo = get_photo(name=10)
#     await bot.edit_message_media(
#         chat_id=callback.message.chat.id,
#         message_id=callback.message.message_id,
#         media=InputMediaPhoto(
#             media=photo,
#             caption=mg
#         ),
#         reply_markup=kb)
#
#
# @router.callback_query(F.data == 'parts')
# async def page_ten(callback: CallbackQuery):
#     await bot.edit_message_media(
#         chat_id=callback.message.chat.id,
#         message_id=callback.message.message_id,
#         media=InputMediaPhoto(
#             media=get_photo(name=11),
#             caption=lexicon['parts']
#         ),
#         reply_markup=keyboard_parts())
#
#
# @router.callback_query(F.data == 'buy_all')
# async def buy_all(callback: CallbackQuery):
#     await bot.edit_message_media(
#         chat_id=callback.message.chat.id,
#         message_id=callback.message.message_id,
#         media=InputMediaPhoto(
#             media=get_photo(name=10),
#             caption=lexicon['buy']
#         ),
#         reply_markup=keyboard_buy())
#
#
# @router.callback_query(F.data == 'help')
# async def help_handler(callback: CallbackQuery):
#     await bot.send_photo(chat_id=callback.from_user.id, photo=get_photo(name=12), caption='Если у вас возникли проблемы, вы можете позвонить по номеру ☎️Тел +79232656553\n'
#                                        'Вам постараются помочь в вашем вопросе')
#
# @router.message(IsPhone())
# async def get_contact(message: Message):
#     contact = message.contact
#     user = await db_manager.get_user(user_id=message.from_user.id)
#     await db_manager.update_user(user_id=message.from_user.id, user_data={'phone': contact.phone_number})
#     await bot.send_message(chat_id=admin_id(), text=f'Пользователь дал согласие на обработку персональных данных.\n'
#                                                     f'Его номер : {contact.phone_number}')
#
#     if user.fio:
#         kb = ReplyKeyboardRemove()
#     else:
#         kb = None
#     await message.answer(f"Ваш номер {contact.phone_number} был получен",
#                          reply_markup=kb)
#
# class FIO(StatesGroup):
#     fio = State()
#
#
# @router.message(F.text == "Отправить ФИО👤")
# async def get_FIO(message: Message, state: FSMContext):
#     await message.answer(lexicon["phone"])
#     await state.set_state(FIO.fio)
#
#
# @router.message(StateFilter(FIO.fio), F.text.split().len() == 3)
# async def add_name(message: Message, state: FSMContext):
#     await state.update_data(fio=message.text)
#     fio = await state.get_data()
#     await db_manager.update_user(user_id=message.chat.id, user_data={'fio': fio['fio']})
#     await state.clear()
#     await message.answer('Ваше ФИО получено и сохранено')
#
#
# @router.message(StateFilter(FIO.fio))
# async def add_not_trips(message: Message):
#     await message.answer(lexicon["phone"])