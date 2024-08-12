import logging

from aiogram import F, Router, Bot
from aiogram.filters import ChatMemberUpdatedFilter, MEMBER, IS_MEMBER, IS_NOT_MEMBER
from aiogram.types import ChatMemberUpdated

from config import db_config
from database.requests import DatabaseManager

logger = logging.getLogger(__name__)
router = Router()
router.message.filter(F.chat.type == 'channel')
dsn = db_config()
db_manager = DatabaseManager(dsn=dsn)


@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def new_members(event: ChatMemberUpdated, bot: Bot):
    if event.new_chat_member.status == 'member':
        user_id = event.from_user.id
        logging.debug(f'New user by id={user_id} in chat')
        member = await db_manager.get_user(user_id=user_id)
        if not member:
            await bot.ban_chat_member(chat_id=-1002150711769, user_id=user_id)
            await bot.unban_chat_member(chat_id=-1002150711769, user_id=user_id)
            logging.debug(f'Kick user by id={user_id}')
