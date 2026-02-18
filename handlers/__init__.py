from aiogram import Dispatcher

from .subscription import router as subscription_router
from .start import router as start_router
from .admin import router as admin_router
from .language import router as language_router
from .invite import router as invite_router
from .messaging import router as messaging_router


def register_all_handlers(dp: Dispatcher) -> None:
    """Регистрация всех роутеров. Порядок важен!"""
    dp.include_router(subscription_router)  # check_sub — первый
    dp.include_router(start_router)
    dp.include_router(admin_router)
    dp.include_router(language_router)
    dp.include_router(invite_router)
    dp.include_router(messaging_router)     # последний — ловит все сообщения
