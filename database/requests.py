import logging

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from bot import bot
from config import admin_id
from database.model import Base, Users, Links
from keyboards import keyboard_friend
from lexicon import lexicon


async def send_admin(status: bool):
    d = {True: 'Договоры для Совершеннолетних', False: 'Договоры для Несовершеннолетних'}
    await bot.send_message(chat_id=admin_id(), text=lexicon['new_links'].format(button=d[status]), reply_markup=keyboard_friend.as_markup(resize_keyboard=True))


class DatabaseManager:
    def __init__(self, dsn):
        self.engine = create_async_engine(dsn, echo=True)
        self.async_session = async_sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)

    async def create_tables(self):
        async with self.async_session() as session:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

    # add new user
    async def add_user(self, user_data):
        try:
            async with self.async_session() as session:
                new_user = Users(**user_data)
                session.add(new_user)
                await session.commit()
                logging.debug(f'New user added with id: {new_user.user_id}')
                return new_user  # Возвращаем объект нового пользователя
        except IntegrityError as e:
            print('ERRRORRR', e)
            logging.debug(f'User with data {user_data} already exists')
            return None  # Возвращаем None, если пользователь уже существует
        except SQLAlchemyError as e:
            logging.error(f'Error occurred while adding user: {str(e)}')

    # get user
    async def get_user(self, user_id):
        async with self.async_session() as session:
            result = await session.execute(select(Users).where(Users.user_id == user_id))
            user = result.scalar()
            logging.debug(f'Get user by id={user_id}')
            return user if user else None

    # get all users
    async def get_users(self):
        async with self.async_session() as session:
            result = await session.execute(select(Users))
            all_users = result.scalars()
            users = [user for user in all_users]
            return users

    # update user
    async def update_user(self, user_data: dict, user_id: int = None) -> None:
        async with self.async_session() as session:
            stmt = update(Users).where(Users.user_id == user_id).values(user_data)
            await session.execute(stmt)
            await session.commit()
            logging.debug(f'Update user by id={user_id}')

    # delete user
    async def delete_user(self, user_id):
        async with self.async_session() as session:
            stmt = delete(Users).where(Users.user_id == user_id)
            await session.execute(stmt)
            await session.commit()
            logging.debug(f'Delete user by id={user_id}')

    async def add_link(self, link):
        try:
            async with self.async_session() as session:
                new_links = Links(**link)
                session.add(new_links)
                await session.commit()
                logging.debug('New link')
        except SQLAlchemyError as e:
            logging.error(f'Error occurred while adding user: {str(e)}')

    async def get_link(self, status):
        async with self.async_session() as session:
            result = await session.execute(select(Links).where(Links.status == status))
            link = result.scalar()
            logging.debug('Get link')
            if link:
                return link
            else:
                await send_admin(status=status)
                return None

    async def delete_link(self, link_id):
        async with self.async_session() as session:
            stmt = delete(Links).where(Links.id_link == link_id)
            await session.execute(stmt)
            await session.commit()
            logging.debug(f'Delete link by id={link_id}')

    async def get_links(self, status: bool):
        try:
            async with self.async_session() as session:
                result = await session.execute(select(Links).where(Links.status == status))
                all_links = result.scalars()
                links = [link for link in all_links]
                return links
        except SQLAlchemyError as e:
            logging.error(f'Error occurred while adding user: {str(e)}')
            await send_admin(status=status)
            return None
