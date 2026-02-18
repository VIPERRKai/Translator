from aiogram import Router, F
from aiogram.types import Message
from db import create_invite, delete_chat
from config import BOT_USERNAME
from keyboards.reply import main_menu_keyboard

router = Router()


# 👇 Ловим текст кнопки "🔗 Создать инвайт"
@router.message(F.text == "🔗 Создать инвайт")
async def handle_create_invite(message: Message):
    invite_code = await create_invite(message.from_user.id)
    link = f"https://t.me/{BOT_USERNAME}?start={invite_code}"

    await message.answer(
        f"🔗 <b>Ваша инвайт-ссылка:</b>\n\n<code>{link}</code>\n\nОтправьте её собеседнику.",
        reply_markup=main_menu_keyboard(message.from_user.id)
    )


# 👇 Ловим текст кнопки "❌ Завершить чат"
@router.message(F.text == "❌ Завершить чат")
async def handle_end_chat(message: Message):
    partner_id = await delete_chat(message.from_user.id)

    if partner_id:
        await message.answer("❌ Чат завершён.", reply_markup=main_menu_keyboard(message.from_user.id))
        await message.bot.send_message(
            partner_id,
            "❌ Собеседник завершил чат.",
            reply_markup=main_menu_keyboard(partner_id)
        )
    else:
        await message.answer("ℹ️ У вас нет активного чата.", reply_markup=main_menu_keyboard(message.from_user.id))