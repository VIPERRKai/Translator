from aiogram import Router, types, F

from db import get_partner_id, get_language
from translator import translate_text
from config import LANGUAGES

router = Router()


@router.message(F.text)
async def handle_text_message(message: types.Message) -> None:
    """Получает текст, переводит и пересылает собеседнику."""
    user_id = message.from_user.id
    partner_id = await get_partner_id(user_id)

    if not partner_id:
        await message.answer(
            "ℹ️ У вас нет активного чата.\n"
            "Создайте инвайт-ссылку или перейдите по ссылке собеседника.",
        )
        return

    sender_lang = await get_language(user_id)
    partner_lang = await get_language(partner_id)

    translated = await translate_text(
        text=message.text,
        source_lang=sender_lang,
        target_lang=partner_lang,
    )

    sender_name = message.from_user.first_name or "User"
    sender_lang_name = LANGUAGES.get(sender_lang, sender_lang)

    await message.bot.send_message(
        partner_id,
        f"💬 <b>{sender_name}</b> <i>({sender_lang_name})</i>:\n\n"
        f"{translated}",
    )

    await message.answer("✅ Сообщение отправлено и переведено.")


@router.message(F.sticker)
async def handle_sticker(message: types.Message) -> None:
    """Пересылает стикеры без перевода."""
    partner_id = await get_partner_id(message.from_user.id)
    if partner_id:
        await message.bot.send_sticker(partner_id, message.sticker.file_id)


@router.message(F.photo)
async def handle_photo(message: types.Message) -> None:
    """Пересылает фото, переводя подпись."""
    partner_id = await get_partner_id(message.from_user.id)
    if not partner_id:
        return

    caption = message.caption or ""
    if caption:
        sender_lang = await get_language(message.from_user.id)
        partner_lang = await get_language(partner_id)
        caption = await translate_text(caption, sender_lang, partner_lang)

    sender_name = message.from_user.first_name or "User"
    full_caption = f"📷 <b>{sender_name}</b>:\n{caption}" if caption else f"📷 <b>{sender_name}</b>"

    await message.bot.send_photo(
        partner_id,
        photo=message.photo[-1].file_id,
        caption=full_caption,
    )
