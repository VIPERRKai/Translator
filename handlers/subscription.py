from aiogram import Router, types, F

from middlewares.subscription import is_subscribed, send_subscribe_message
from keyboards.inline import main_menu_keyboard

router = Router()


@router.callback_query(F.data == "check_sub")
async def cb_check_sub(callback: types.CallbackQuery) -> None:
    """Проверка подписки на канал."""
    if await is_subscribed(callback.bot, callback.from_user.id):
        await callback.answer("✅ Подписка подтверждена!", show_alert=False)
        await callback.message.delete()
        await callback.message.answer(
            "✅ Спасибо за подписку!\n\n"
            "Теперь вы можете пользоваться ботом 🚀",
            reply_markup=main_menu_keyboard(callback.from_user.id),
        )
    else:
        await callback.answer(
            "❌ Вы не подписаны на канал! Подпишитесь и попробуйте снова.",
            show_alert=True,
        )
