from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


page_2 = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(
        text='Почему мы? 🚀',
        callback_data='page_2'
    )]]
)

page_3 = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(
        text='Как нас найти 📍',
        callback_data='page_3'
    )]]
)

page_4 = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(
        text="Как стать учеником 🚀",
        callback_data='page_4'
    )]]
)

page_5 = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(
        text="1. Подписать Договор📑",
        callback_data='page_5'
    )]]
)

doc = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(
        text='Оформить договор 📄',
        url='https://desktop.doki.online/contract/66b5f59c5b7d59d6216d790f',
        callback_data='doc'
    )]]
)

doc_yes = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(
        text='Договор отправил ✔️',
        callback_data='doc_yes'
    )]]
)
