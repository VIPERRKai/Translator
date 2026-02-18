from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware, Bot
from aiogram.types import (
    CallbackQuery,
    Message,
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.enums import ChatMemberStatus

from config import CHANNEL_ID, CHANNEL_URL
from db import get_setting


async def is_subscribed(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in (
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR,
        )
    except Exception:
        return False


def subscribe_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Подписаться", url=CHANNEL_URL)],
        [InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_sub")],
    ])


async def send_subscribe_message(target, bot: Bot) -> None:
    """Отправляет сообщение о подписке с текстом и медиа из настроек."""
    sub_text = await get_setting("sub_text")
    sub_media = await get_setting("sub_media")
    sub_media_type = await get_setting("sub_media_type")
    kb = subscribe_keyboard()

    if isinstance(target, Message):
        chat_id = target.chat.id
    elif isinstance(target, CallbackQuery):
        chat_id = target.message.chat.id
    else:
        return

    if sub_media and sub_media_type:
        if sub_media_type == "photo":
            await bot.send_photo(
                chat_id=chat_id,
                photo=sub_media,
                caption=sub_text,
                reply_markup=kb,
            )
        elif sub_media_type == "animation":
            await bot.send_animation(
                chat_id=chat_id,
                animation=sub_media,
                caption=sub_text,
                reply_markup=kb,
            )
    else:
        await bot.send_message(
            chat_id=chat_id,
            text=sub_text,
            reply_markup=kb,
        )


class SubscriptionMessageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id
        bot: Bot = data["bot"]

        # Разрешаем check_sub callback проходить всегда (это Message middleware)
        if await is_subscribed(bot, user_id):
            return await handler(event, data)

        await send_subscribe_message(event, bot)
        return None


class SubscriptionCallbackMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[CallbackQuery, dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: dict[str, Any],
    ) -> Any:
        # Всегда пропускаем check_sub
        if event.data == "check_sub":
            return await handler(event, data)

        user_id = event.from_user.id
        bot: Bot = data["bot"]

        if await is_subscribed(bot, user_id):
            return await handler(event, data)

        await event.answer("📢 Сначала подпишитесь на канал!", show_alert=True)
        await send_subscribe_message(event, bot)
        return None
