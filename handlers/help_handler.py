from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.state import default_state
from aiogram.types import Message

from database.requests import DatabaseManager
from lexicon import lexicon
from config import db_config

router = Router()
router.message.filter(F.chat.type == 'private')
dsn = db_config()
db_manager = DatabaseManager(dsn=dsn)


@router.message(F.text == '/help', StateFilter(default_state))
async def start_command(message: Message):
    await message.answer(lexicon['help'])
