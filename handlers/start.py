from aiogram import Router, types
from aiogram.filters import CommandStart, CommandObject

from db import upsert_user, accept_invite, get_language
from keyboards.inline import main_menu_keyboard, language_keyboard
from config import LANGUAGES

router = Router()


@router.message(CommandStart(deep_link=True))
async def cmd_start_deep(message: types.Message, command: CommandObject) -> None:
    """Пользователь перешёл по invite deep-link."""
    # Удаляем /start от пользователя
    try:
        await message.delete()
    except Exception:
        pass

    user = message.from_user
    await upsert_user(user.id, user.username)

    invite_code = command.args
    if not invite_code:
        await message.answer("❌ Некорректная ссылка.")
        return

    # Просим выбрать язык
    await message.answer(
        "👋 Добро пожаловать!\n\n"
        "Прежде чем начать общение, выберите <b>ваш язык</b>:",
        reply_markup=language_keyboard(),
    )

    # Пытаемся принять инвайт
    chat = await accept_invite(invite_code, user.id)
    if chat:
        partner_id = chat["user1_id"]
        partner_lang = await get_language(partner_id)
        lang_name = LANGUAGES.get(partner_lang, partner_lang)

        await message.answer(
            f"✅ Вы подключились к чату!\n"
            f"Собеседник общается на <b>{lang_name}</b>.\n\n"
            f"Просто отправляйте сообщения — они будут автоматически переведены 🚀",
            reply_markup=main_menu_keyboard(user.id),
        )

        await message.bot.send_message(
            partner_id,
            "🎉 К вашему чату присоединился собеседник!\n"
            "Отправляйте сообщения — они будут автоматически переведены 🚀",
            reply_markup=main_menu_keyboard(partner_id),
        )
    else:
        await message.answer(
            "⚠️ Инвайт-ссылка недействительна или уже использована.",
            reply_markup=main_menu_keyboard(user.id),
        )


@router.message(CommandStart(deep_link=False))
async def cmd_start(message: types.Message) -> None:
    """Обычный /start без deep-link."""
    # Удаляем /start от пользователя
    try:
        await message.delete()
    except Exception:
        pass

    user = message.from_user
    await upsert_user(user.id, user.username)

    await message.answer(
        f"👋 Привет, <b>{user.first_name}</b>!\n\n"
        "Я бот для общения на разных языках.\n\n"
        "1️⃣ Установите <b>свой язык</b> кнопкой «🌐 Мой язык»\n"
        "2️⃣ Создайте <b>инвайт-ссылку</b> и отправьте собеседнику\n"
        "3️⃣ Пишите сообщения — бот переведёт их автоматически 🚀",
        reply_markup=main_menu_keyboard(user.id),
    )
