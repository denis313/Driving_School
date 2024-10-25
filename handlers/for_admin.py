from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram.types import Message, CallbackQuery, InputMediaPhoto

from config import db_config
from database.requests import DatabaseManager
from handlers.filter import IsAdmin
from keyboards import CallbackFactory, keyboard_buy, admin_kb
from lexicon import lexicon
from service import get_photo, send_link, filter_url

router = Router()
router.message.filter(IsAdmin())
dsn = db_config()
db_manager = DatabaseManager(dsn=dsn)


@router.callback_query(CallbackFactory.filter())
async def payments(callback: CallbackQuery, callback_data: CallbackFactory, bot: Bot):
    await bot.edit_message_media(
        chat_id=callback_data.user_id,
        message_id=callback_data.mg,
        media=InputMediaPhoto(
            media=get_photo(name='buy'),
            caption=lexicon['buy']
        ),
        reply_markup=keyboard_buy())
    await db_manager.update_user(user_id=callback_data.user_id, user_data={'buy': True})
    await callback.message.answer('Возможность оплатить предоставлена✅')


class Link(StatesGroup):
    links = State()
    status = State()


@router.message(F.text.in_(lexicon['button']), StateFilter(default_state))
async def get_links(message: Message, state: FSMContext):
    if message.text == lexicon['button'][0]:
        mg = lexicon['links_17']
        st = False
    else:
        mg = lexicon['links_18']
        st = True
    await state.update_data(status=st)
    await state.set_state(Link.links)
    await message.answer(mg)


@router.message(StateFilter(Link.links))
async def add_list(message: Message, state: FSMContext):
    await state.update_data(links=message.text)
    data = await state.get_data()
    valid_link = False
    mg = 'Ссылки не приняты ❌'
    for link in data['links'].split(','):
        if filter_url(url=link):
            flag = await send_link(status=data['status'], link=link)
            if flag is False:
                await db_manager.add_link(link={'status': data['status'], 'link': link.strip()})
            valid_link = True
        else:
            await message.answer(f'Похоже что вы отправили что-то не то, это <b>{link}</b> не ссылка')
    await state.clear()
    if valid_link:
        mg = 'Ссылки приняты✅'
    await message.answer(mg)



@router.callback_query(F.data == 'sent_links')
async def payments(callback: CallbackQuery, bot: Bot):
    users = await db_manager.get_users_links()
    mg = ''
    try:
        if users:
            for user in users:
                if user.doc is not None:
                    mg += f'Номер: {user.phone} - ссылка {user.doc}\n'
            if mg:  # Проверка, есть ли сформированные данные
                await bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                            text=mg, reply_markup=admin_kb())
            else:
                await bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                            text="Нет доступных ссылок.", reply_markup=admin_kb())
        else:
            await bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                        text="Нет пользователей.", reply_markup=admin_kb())
    except Exception as e:
        print(f"Ошибка: {e}")

    # await bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id, text='Ссылки не отправляли',
    #                             reply_markup=admin_kb())


@router.callback_query(F.data == 'rest_links')
async def payments(callback: CallbackQuery, bot: Bot):
    d = {True: 'Договоры для Совершеннолетних', False: 'Договоры для Несовершеннолетних'}
    count = 0
    mg = ''
    try:
        for key, item in d.items():
            links = await db_manager.get_links(status=key)
            if links:  # Проверяем, есть ли ссылки для текущей категории
                count += len(links)
                for link in links:
                    mg += f'{item} - {link.link}\n'  # Используем item вместо d[key]
            else:
                mg += f'{item} - Нет доступных ссылок\n'

        if mg:
            await bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                        text=f'Всего ссылок - {count}\n' + mg, reply_markup=admin_kb())
        else:
            await bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id,
                                        text='Ссылок нет.', reply_markup=admin_kb())
    except Exception as e:
        print(f"Ошибка: {e}")
