from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery

from bot import bot
from config import db_config, admin_id
from database.requests import DatabaseManager
from keyboards import keyboard_page_2, keyboard_page_3, keyboard_page_4, keyboard_page_5, keyboard_parts, allow_payment, \
    back, keyboard_buy, keyboard_page_6, keyboard_friend, \
    keyboard_page_7, keyboard_page_8
from lexicon import lexicon

router = Router()
router.message.filter(F.chat.type == 'private')
dsn = db_config()
db_manager = DatabaseManager(dsn=dsn)


@router.message(CommandStart(), StateFilter(default_state))
async def page_one(message: Message):
    await db_manager.create_tables()
    await message.answer(lexicon['start'], reply_markup=keyboard_page_2())
    if str(message.from_user.id) == admin_id():
        await message.answer("Вы администратор", reply_markup=keyboard_friend.as_markup(resize_keyboard=True))


@router.callback_query(F.data == 'page_2')
async def page_two(callback: CallbackQuery):
    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text=lexicon['two'], reply_markup=keyboard_page_3())


@router.callback_query(F.data == 'page_3')
async def page_three(callback: CallbackQuery):
    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text=lexicon['three'], reply_markup=keyboard_page_4())


@router.callback_query(F.data == 'page_4')
async def page_four(callback: CallbackQuery):
    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text=lexicon['four'], reply_markup=keyboard_page_5())


@router.callback_query(F.data == 'page_5')
async def page_fife(callback: CallbackQuery):
    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text=lexicon['fife'], reply_markup=keyboard_page_6())
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
    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text=lexicon['six'], reply_markup=keyboard_page_7())


@router.callback_query(F.data == 'page_7')
async def page_seven(callback: CallbackQuery):
    user = await db_manager.get_user(user_id=callback.from_user.id)
    if user.doc:
        mg = lexicon['seven'].format(url=user.doc)
    else:
        link = await db_manager.get_link(status=user.adult)
        await db_manager.update_user(user_id=callback.from_user.id, user_data={'doc': str(link.link)})
        await db_manager.delete_link(link_id=link.id_link)
        mg = lexicon['seven'].format(url=link.link)
    if user.adult:
        page = 'adult'
    else:
        page = 'no_adult'
    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text=mg,
                                reply_markup=keyboard_page_8(page=page))


@router.callback_query(F.data == 'page_8')
async def page_eight(callback: CallbackQuery):
    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text=lexicon['waiting'], reply_markup=back(page='page_7'))
    print(admin_id(), 'admin')
    await bot.send_message(chat_id=admin_id(), text=lexicon['for_admin_2'],
                           reply_markup=allow_payment(user_id=callback.from_user.id,
                                                      mg_id=callback.message.message_id))


@router.callback_query(F.data == 'parts')
async def page_nine(callback: CallbackQuery):
    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text=lexicon['parts'], reply_markup=keyboard_parts())


@router.callback_query(F.data == 'buy_all')
async def buy_all(callback: CallbackQuery):
    await bot.edit_message_text(chat_id=callback.from_user.id,
                                message_id=callback.message.message_id,
                                text=lexicon['buy'],
                                reply_markup=keyboard_buy())
