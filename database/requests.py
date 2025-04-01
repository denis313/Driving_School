import logging

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from bot import bot
from config import admin_id
from database.model import Base, Users, Links, Prices, TBank_Links
from keyboards import keyboard_friend
from lexicon import lexicon


async def send_admin(status: bool):
    d = {True: 'Договоры для Совершеннолетних', False: 'Договоры для Несовершеннолетних'}
    await bot.send_message(chat_id=admin_id(), text=lexicon['new_links'].format(button=d[status]),
                           reply_markup=keyboard_friend.as_markup(resize_keyboard=True))


async def send_admin_2(percent: int):
    await bot.send_message(chat_id=admin_id(), text=lexicon['new_tblinks'].format(percent=percent),
                           reply_markup=keyboard_friend.as_markup(resize_keyboard=True))


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

    async def get_users_links(self):
        async with self.async_session() as session:
            # Предположим, что есть поле created_at или ID, по которому можно сортировать пользователей
            result = await session.execute(
                select(Users).order_by(Users.user_id.desc()).limit(30)
            )
            all_users = result.scalars()
            users = [user for user in all_users]
            return users

        # get user
    async def get_prices(self) -> Prices | None:
        async with self.async_session() as session:
            result = await session.execute(select(Prices).where(Prices.id_value == 1))
            prices = result.scalar()
            logging.debug(f'Get prices: {prices.prepayment}, {prices.price}')
            return prices if prices else None

    # update user
    async def update_prices(self, new_prices) -> None:
        async with self.async_session() as session:
            stmt = update(Prices).where(Prices.id_value == 1).values(new_prices)
            await session.execute(stmt)
            await session.commit()
            logging.debug(f'Update prices')

    #add tbank link
    async def add_tblink(self, link):
        try:
            async with self.async_session() as session:
                new_links = TBank_Links(**link)
                session.add(new_links)
                await session.commit()
                logging.debug('New link')
        except SQLAlchemyError as e:
            logging.error(f'Error occurred while adding user: {str(e)}')

    # get tbank link
    async def get_tblink(self, percent: int):
        async with self.async_session() as session:
            result = await session.execute(select(TBank_Links).where(TBank_Links.percent==percent))
            link = result.scalar()
            logging.debug('Get link')
            if link:
                return link
            else:
                await send_admin_2(percent=percent)
                return None

    # get link by id
    # get tbank link
    async def get_tblink_by_linkid(self, id_link: int):
        async with self.async_session() as session:
            result = await session.execute(select(TBank_Links).where(TBank_Links.id_link == id_link))
            link = result.scalar()
            logging.debug('Get link')
            if link:
                return link
            else:
                return None

    # delete tbank link
    async def delete_tblink(self, link_id):
        async with self.async_session() as session:
            stmt = delete(TBank_Links).where(TBank_Links.id_link == link_id)
            await session.execute(stmt)
            await session.commit()
            logging.debug(f'Delete link by id={link_id}')

    # get tbank links
    async def get_tblinks(self, percent: int):
        try:
            async with self.async_session() as session:
                result = await session.execute(select(TBank_Links).where(TBank_Links.percent == percent))
                all_links = result.scalars()
                links = [link for link in all_links]
                return links
        except SQLAlchemyError as e:
            logging.error(f'Error occurred while adding user: {str(e)}')
            await send_admin_2(percent)
            return None