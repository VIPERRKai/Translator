from aiogram import Router, types, F

from db import set_language, get_language
from keyboards.inline import language_keyboard, main_menu_keyboard
from config import LANGUAGES

router = Router()


@router.callback_query(F.data == "my_lang")
async def cb_my_lang(callback: types.CallbackQuery) -> None:
    current = await get_language(callback.from_user.id)
    lang_name = LANGUAGES.get(current, current)

    await callback.message.edit_text(
        f"🌐 Ваш текущий язык: <b>{lang_name}</b>\n\n"
        "Выберите новый язык:",
        reply_markup=language_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_lang:"))
async def cb_set_lang(callback: types.CallbackQuery) -> None:
    lang_code = callback.data.split(":")[1]
    if lang_code not in LANGUAGES:
        await callback.answer("❌ Неизвестный язык", show_alert=True)
        return

    await set_language(callback.from_user.id, lang_code)
    lang_name = LANGUAGES[lang_code]

    await callback.message.edit_text(
        f"✅ Язык установлен: <b>{lang_name}</b>\n\n"
        "Все входящие сообщения будут переводиться на этот язык.",
        reply_markup=main_menu_keyboard(callback.from_user.id),
    )
    await callback.answer(f"Язык: {lang_name}")
