from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from db import get_language, set_language
from config import LANGUAGES
from keyboards.inline import language_keyboard
from keyboards.reply import main_menu_keyboard

router = Router()


# 👇 Ловим текст кнопки "🌐 Мой язык"
@router.message(F.text == "🌐 Мой язык")
async def handle_my_lang(message: Message):
    current = await get_language(message.from_user.id)
    lang_name = LANGUAGES.get(current, current)

    # Отправляем инлайн-кнопки (флаги), так как их много и они не влезут в нижнее меню
    await message.answer(
        f"🌐 Ваш текущий язык: <b>{lang_name}</b>\n\nВыберите новый язык из списка:",
        reply_markup=language_keyboard()
    )


@router.callback_query(F.data.startswith("set_lang:"))
async def cb_set_lang(callback: CallbackQuery):
    lang_code = callback.data.split(":")[1]
    if lang_code not in LANGUAGES:
        await callback.answer("❌ Неизвестный язык", show_alert=True)
        return

    await set_language(callback.from_user.id, lang_code)
    lang_name = LANGUAGES[lang_code]

    # Удаляем сообщение с флагами, чтобы не засорять чат
    await callback.message.delete()

    await callback.message.answer(
        f"✅ Язык установлен: <b>{lang_name}</b>",
        reply_markup=main_menu_keyboard(callback.from_user.id)
    )
    await callback.answer()