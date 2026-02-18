import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from db import create_pool, close_pool
from handlers import register_all_handlers
from middlewares.subscription import (
    SubscriptionMessageMiddleware,
    SubscriptionCallbackMiddleware,
)

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    await create_pool()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Middleware проверки подписки на канал
    dp.message.middleware(SubscriptionMessageMiddleware())
    dp.callback_query.middleware(SubscriptionCallbackMiddleware())

    register_all_handlers(dp)

    try:
        logging.info("Bot started!")
        await dp.start_polling(bot)
    finally:
        await close_pool()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
