from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery

from CRM.bot import bot
from database.requests import DatabaseManager
from keyboards import page_2, page_3, page_4, doc, page_5
from lexicon import lexicon
from config import db_config

router = Router()
router.message.filter(F.chat.type == 'private')
dsn = db_config()
db_manager = DatabaseManager(dsn=dsn)


@router.message(CommandStart(), StateFilter(default_state))
async def page_one(message: Message):
    # await db_manager.create_tables()
    await message.answer(lexicon['start'], reply_markup=page_2)


@router.callback_query(F.data == 'page_2')
async def page_two(callback: CallbackQuery):
    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text=lexicon['three'], reply_markup=page_3)


@router.callback_query(F.data == 'page_3')
async def page_three(callback: CallbackQuery):
    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text=lexicon['where'], reply_markup=page_4)


@router.callback_query(F.data == 'page_4')
async def page_four(callback: CallbackQuery):
    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text=lexicon['children'], reply_markup=page_5)


@router.callback_query(F.data == 'page_5')
async def page_fife(callback: CallbackQuery):
    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text=lexicon['doc'], reply_markup=doc)
