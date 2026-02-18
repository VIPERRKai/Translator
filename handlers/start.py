from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message
from db import upsert_user, accept_invite, get_language
from config import LANGUAGES
# 👇 Импортируем новую клавиатуру
from keyboards.reply import main_menu_keyboard

router = Router()


@router.message(CommandStart(deep_link=True))
async def cmd_start_deep(message: Message, command: CommandObject):
    user = message.from_user
    await upsert_user(user.id, user.username)
    invite_code = command.args

    if not invite_code:
        await message.answer("❌ Некорректная ссылка.")
        return

    # Отправляем сообщение с нижней клавиатурой
    await message.answer("👋 Добро пожаловать!", reply_markup=main_menu_keyboard(user.id))

    chat = await accept_invite(invite_code, user.id)
    if chat:
        partner_id = chat["user1_id"]
        partner_lang = await get_language(partner_id)
        lang_name = LANGUAGES.get(partner_lang, partner_lang)

        await message.answer(
            f"✅ Вы подключились к чату!\nСобеседник общается на <b>{lang_name}</b>.\n\nПросто отправляйте сообщения 🚀",
            reply_markup=main_menu_keyboard(user.id)
        )
        await message.bot.send_message(
            partner_id,
            "🎉 К вашему чату присоединился собеседник!",
            reply_markup=main_menu_keyboard(partner_id)
        )
    else:
        await message.answer("⚠️ Инвайт-ссылка недействительна.", reply_markup=main_menu_keyboard(user.id))


@router.message(CommandStart(deep_link=False))
async def cmd_start(message: Message):
    user = message.from_user
    await upsert_user(user.id, user.username)

    await message.answer(
        f"👋 Привет, <b>{user.first_name}</b>!\n\n"
        "Выберите действие в меню внизу 👇",
        reply_markup=main_menu_keyboard(user.id)
    )