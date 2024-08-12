from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.state import default_state
from aiogram.types import Message

from lexicon import lexicon

router = Router()
router.message.filter(F.chat.type == 'private')


@router.message(StateFilter(default_state))
async def start_command(message: Message):
    await message.answer(lexicon['other'])
