from aiogram import Router, F
from aiogram.types import CallbackQuery
from middlewares.subscription import is_subscribed
# 👇 БЫЛО: from keyboards.inline import main_menu_keyboard
# 👇 СТАЛО:
from keyboards.reply import main_menu_keyboard

router = Router()


@router.callback_query(F.data == "check_sub")
async def cb_check_sub(callback: CallbackQuery):
    if await is_subscribed(callback.bot, callback.from_user.id):
        await callback.answer("✅ Подписка подтверждена!", show_alert=False)
        try:
            await callback.message.delete()
        except:
            pass

        await callback.message.answer(
            "✅ Спасибо за подписку!\n\nТеперь вы можете пользоваться ботом 🚀",
            reply_markup=main_menu_keyboard(callback.from_user.id)
        )
    else:
        await callback.answer("❌ Вы не подписаны на канал!", show_alert=True)