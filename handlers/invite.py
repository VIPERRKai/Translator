from aiogram import Router, types, F

from db import create_invite, delete_chat
from keyboards.inline import main_menu_keyboard
from config import BOT_USERNAME

router = Router()


@router.callback_query(F.data == "create_invite")
async def cb_create_invite(callback: types.CallbackQuery) -> None:
    invite_code = await create_invite(callback.from_user.id)
    link = f"https://t.me/{BOT_USERNAME}?start={invite_code}"

    await callback.message.edit_text(
        "🔗 <b>Ваша инвайт-ссылка:</b>\n\n"
        f"<code>{link}</code>\n\n"
        "Отправьте эту ссылку собеседнику.\n"
        "Когда он перейдёт по ней — чат начнётся автоматически 🚀",
        reply_markup=main_menu_keyboard(callback.from_user.id),
    )
    await callback.answer()


@router.callback_query(F.data == "end_chat")
async def cb_end_chat(callback: types.CallbackQuery) -> None:
    partner_id = await delete_chat(callback.from_user.id)

    if partner_id:
        await callback.message.edit_text(
            "❌ Чат завершён.",
            reply_markup=main_menu_keyboard(callback.from_user.id),
        )
        await callback.bot.send_message(
            partner_id,
            "❌ Собеседник завершил чат.",
            reply_markup=main_menu_keyboard(partner_id),
        )
    else:
        await callback.message.edit_text(
            "ℹ️ У вас нет активного чата.",
            reply_markup=main_menu_keyboard(callback.from_user.id),
        )
    await callback.answer()
