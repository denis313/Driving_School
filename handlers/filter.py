from aiogram.filters import BaseFilter
from aiogram.types import Message

from config import admin_id


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message):
        return str(message.chat.id) == admin_id()
