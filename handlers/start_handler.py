from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery, InputMediaPhoto

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
    await message.answer_photo(photo="AgACAgIAAxkBAAEUSE1mzeroqnLnug735lRDrdIkeMh1TgAC0-AxG2hucEoYqWgK1M1SowEAAwIAA3gAAzUE", caption=lexicon['start'], reply_markup=keyboard_page_2())
    if str(message.from_user.id) == admin_id():
        await message.answer("Вы администратор", reply_markup=keyboard_friend.as_markup(resize_keyboard=True))


@router.callback_query(F.data == 'page_2')
async def page_two(callback: CallbackQuery):
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(
            media="AgACAgIAAxkBAAEUR8NmzbumqUCcUTBoRSci7hTljpsK1gAC--QxG1YjaEpZfGl2SoKowgEAAwIAA3MAAzUE",
            caption=lexicon['two']
        ),
        reply_markup=keyboard_page_3())


@router.callback_query(F.data == 'page_3')
async def page_three(callback: CallbackQuery):
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(
            media="AgACAgIAAxkBAAEUSFBmzetQxRqflSrqzjdgmuB8Wl0vewAC1OAxG2hucEqeJFXjpGwX2gEAAwIAA3gAAzUE",
            caption=lexicon['three']
        ),
        reply_markup=keyboard_page_4())


@router.callback_query(F.data == 'page_4')
async def page_four(callback: CallbackQuery):
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(
            media="AgACAgIAAxkBAAEUSMtmzg2ovCM3JgnI-Sv71aCJI9zJcgACJ-IxG2hucErzWb3_Qh56_wEAAwIAA3gAAzUE",
            caption=lexicon['four']
        ),
        reply_markup=keyboard_page_5())


@router.callback_query(F.data == 'page_5')
async def page_fife(callback: CallbackQuery):
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(
            media="AgACAgIAAxkBAAEUSMlmzgzXWKIGbTA5bnOz8BMbBf93pQACIOIxG2hucEqZDSkd6YKTOQEAAwIAA3gAAzUE",
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
            media="AgACAgIAAxkBAAEUSNVmzg7ycI4SGDorCizD3FeT_FIimgACOuIxG2hucEoe75ExUDXxzAEAAwIAA3gAAzUE",
            caption=lexicon['six']
        ),
        reply_markup=keyboard_page_7())


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
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(
            media="AgACAgIAAxkBAAEUSI1mzfxTYDYwCHx6e_DPeyI2KC0wdgACNOExG2hucErujeMY3hldzQEAAwIAA3gAAzUE",
            caption=mg
        ),
        reply_markup=keyboard_page_8(page=page))


@router.callback_query(F.data == 'page_8')
async def page_eight(callback: CallbackQuery):
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(
            media="AgACAgIAAxkBAAEUSNxmzhGOuDly_q7dKr586dSW1hBrwAACnOIxG2hucErqhMx9oyqpOgEAAwIAA3gAAzUE",
            caption=lexicon['eight']
        ),
        reply_markup=back(page='page_7'))
    await bot.send_message(chat_id=admin_id(), text=lexicon['for_admin_2'],
                           reply_markup=allow_payment(user_id=callback.from_user.id,
                                                      mg_id=callback.message.message_id))


@router.callback_query(F.data == 'parts')
async def page_nine(callback: CallbackQuery):
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(
            media="AgACAgIAAxkBAAEUSOZmzhRpb-udnSme8ZPkugJAzw6d5QACteIxG2hucEosbEuiWNgUSQEAAwIAA3gAAzUE",
            caption=lexicon['parts']
        ),
        reply_markup=keyboard_parts())


@router.callback_query(F.data == 'buy_all')
async def buy_all(callback: CallbackQuery):
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(
            media="AgACAgIAAxkBAAEUSORmzhPYYRENasJzgMsyHaeCu6v_SQACsOIxG2hucEo8ld5QEOW9PAEAAwIAA3kAAzUE",
            caption=lexicon['buy']
        ),
        reply_markup=keyboard_buy())
