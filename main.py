import asyncio
import logging
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Dispatcher

from CRM.bot import bot

from handlers import start_handler, handler_buy, check_handler, help_handler, other_handler

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main():
    # Конфигурируем логирование
    logging.basicConfig(level=logging.DEBUG,
                        filename="py_log.log",
                        filemode="w",
                        format='[%(asctime)s] #%(levelname)-8s %(filename)s:%(lineno)d - %(name)s - %(message)s')

    # Инициализируем бот и диспетчер
    dp = Dispatcher()

    # Регистриуем роутеры в диспетчере
    dp.include_routers(start_handler.router, help_handler.router, handler_buy.router, check_handler.router,
                       other_handler.router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("stopped")
