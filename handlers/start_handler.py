import logging

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery, InputMediaPhoto

from amocrm.v2 import Lead
from bot import bot
from config import db_config, admin_id
from database.requests import DatabaseManager
from keyboards import keyboard_page_2, keyboard_page_3, keyboard_page_4, keyboard_page_5, keyboard_parts, allow_payment, \
    back, keyboard_buy, keyboard_page_6, keyboard_friend, \
    keyboard_page_7, keyboard_page_8
from lexicon import lexicon
from photo.get_photo import get_photo

router = Router()
router.message.filter(F.chat.type == 'private')
dsn = db_config()
db_manager = DatabaseManager(dsn=dsn)


@router.message(CommandStart(), StateFilter(default_state))
async def page_one(message: Message):
    await db_manager.create_tables()
    await bot.send_photo(chat_id=message.from_user.id, photo=get_photo(name=1), caption=lexicon['start'], reply_markup=keyboard_page_2())
    if str(message.from_user.id) == admin_id():
        await message.answer("Вы администратор", reply_markup=keyboard_friend.as_markup(resize_keyboard=True))


@router.callback_query(F.data == 'page_2')
async def page_two(callback: CallbackQuery):
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(
            media=get_photo(name=2),
            caption=lexicon['two']
        ),
        reply_markup=keyboard_page_3())


@router.callback_query(F.data == 'next_photo')
async def handle_next_photo(callback: CallbackQuery):
    try:
        await bot.edit_message_media(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            media=InputMediaPhoto(
                media=get_photo(name='next'),
                caption=lexicon['two']
            ),
            reply_markup=keyboard_page_3())
    except TelegramBadRequest:
        pass


@router.callback_query(F.data == 'page_3')
async def page_three(callback: CallbackQuery):
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(
            media=get_photo(name=3),
            caption=lexicon['three']
        ),
        reply_markup=keyboard_page_4())


@router.callback_query(F.data == 'page_4')
async def page_four(callback: CallbackQuery):
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(
            media=get_photo(name=4),
            caption=lexicon['four']
        ),
        reply_markup=keyboard_page_5())


@router.callback_query(F.data == 'page_5')
async def page_fife(callback: CallbackQuery):
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(
            media=get_photo(name=5),
            caption=lexicon['fife']
        ),
        reply_markup=keyboard_page_6())
    await db_manager.add_user(user_data={'user_id': callback.from_user.id})


@router.callback_query(F.data.in_({'adult', 'no_adult'}))
async def page_six(callback: CallbackQuery):
    user = await db_manager.get_user(user_id=callback.from_user.id)
    if user.doc is None:
        if callback.data == 'adult':
            adult = True
        else:
            adult = False
        await db_manager.update_user(user_id=callback.from_user.id, user_data={'adult': adult})
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(
            media=get_photo(name=6),
            caption=lexicon['six']
        ),
        reply_markup=keyboard_page_7())


@router.callback_query(F.data == 'page_7')
async def page_seven(callback: CallbackQuery):
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    user = await db_manager.get_user(user_id=user_id) # Получаем данные пользователя
    page = 'adult' if user.adult else 'no_adult' # Определяем страницу для клавиатуры
    kb = keyboard_page_8(page=page)
    link = await db_manager.get_link(status=user.adult) # Получаем ссылку на основе статуса возраста
    mg = lexicon['waiting'] # Инициализируем переменную mg на случай, если ни одно из условий не выполнится
    if user.doc:
        mg = lexicon['seven'].format(url=user.doc)  # Если документ уже существует
    elif link:
        await db_manager.update_user(user_id=user_id, user_data={'doc': str(link.link)}) # Обновляем данные пользователя и удаляем использованную ссылку
        await db_manager.delete_link(link_id=link.id_link)
        mg = lexicon['seven'].format(url=link.link)
    else:
        kb = back(page='page_5') # Если ссылка не найдена, используем альтернативный текст
    await bot.edit_message_media(
        chat_id=chat_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=get_photo(name=7),
            caption=mg
        ),
        reply_markup=kb
    )


@router.callback_query(F.data == 'page_8')
async def page_eight(callback: CallbackQuery):
    user = await db_manager.get_user(user_id=callback.from_user.id)
    if user.buy is False:
        kb = back(page='page_7')
        mg = lexicon['eight']
        photo = get_photo(name=8)
        await bot.send_message(chat_id=admin_id(), text=lexicon['for_admin_2'],
                               reply_markup=allow_payment(user_id=callback.from_user.id,
                                                          mg_id=callback.message.message_id))
    else:
        kb = keyboard_buy()
        mg = lexicon['buy']
        photo = get_photo(name=9)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(
            media=photo,
            caption=mg
        ),
        reply_markup=kb)


@router.callback_query(F.data == 'parts')
async def page_nine(callback: CallbackQuery):
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(
            media=get_photo(name=10),
            caption=lexicon['parts']
        ),
        reply_markup=keyboard_parts())


@router.callback_query(F.data == 'buy_all')
async def buy_all(callback: CallbackQuery):
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(
            media=get_photo(name=9),
            caption=lexicon['buy']
        ),
        reply_markup=keyboard_buy())
