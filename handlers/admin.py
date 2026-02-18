from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_ID
from db import get_total_users, get_active_chats, get_setting, set_setting
from keyboards.inline import admin_panel_keyboard, main_menu_keyboard

router = Router()


class AdminStates(StatesGroup):
    waiting_sub_text = State()
    waiting_sub_media = State()


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


# ───────── Админ-панель ─────────

@router.callback_query(F.data == "admin_panel")
async def cb_admin_panel(callback: types.CallbackQuery, state: FSMContext) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    await state.clear()
    await callback.message.edit_text(
        "⚙️ <b>Админ-панель</b>\n\n"
        "Выберите действие:",
        reply_markup=admin_panel_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin_back")
async def cb_admin_back(callback: types.CallbackQuery, state: FSMContext) -> None:
    if not is_admin(callback.from_user.id):
        return
    await state.clear()
    await callback.message.edit_text(
        "🏠 <b>Главное меню</b>",
        reply_markup=main_menu_keyboard(callback.from_user.id),
    )
    await callback.answer()


# ───────── Статистика ─────────

@router.callback_query(F.data == "admin_stats")
async def cb_admin_stats(callback: types.CallbackQuery) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    total_users = await get_total_users()
    active_chats = await get_active_chats()

    await callback.message.edit_text(
        "📊 <b>Статистика бота</b>\n\n"
        f"👥 Всего пользователей: <b>{total_users}</b>\n"
        f"💬 Активных чатов: <b>{active_chats}</b>",
        reply_markup=admin_panel_keyboard(),
    )
    await callback.answer()


# ───────── Изменить текст подписки ─────────

@router.callback_query(F.data == "admin_edit_sub_text")
async def cb_edit_sub_text(callback: types.CallbackQuery, state: FSMContext) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    current_text = await get_setting("sub_text")
    await callback.message.edit_text(
        "✏️ <b>Изменение текста подписки</b>\n\n"
        f"Текущий текст:\n<blockquote>{current_text}</blockquote>\n\n"
        "Отправьте новый текст (поддерживается HTML-разметка).\n"
        "Или нажмите «🔙 Назад» для отмены.",
        reply_markup=admin_panel_keyboard(),
    )
    await state.set_state(AdminStates.waiting_sub_text)
    await callback.answer()


@router.message(AdminStates.waiting_sub_text, F.text)
async def handle_new_sub_text(message: types.Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        return

    await set_setting("sub_text", message.text)
    await state.clear()
    await message.answer(
        "✅ Текст подписки обновлён!\n\n"
        f"Новый текст:\n<blockquote>{message.text}</blockquote>",
        reply_markup=admin_panel_keyboard(),
    )


# ───────── Изменить медиа подписки ─────────

@router.callback_query(F.data == "admin_edit_sub_media")
async def cb_edit_sub_media(callback: types.CallbackQuery, state: FSMContext) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    current_media = await get_setting("sub_media")
    current_type = await get_setting("sub_media_type")
    status = f"📎 Текущее медиа: <b>{current_type or 'не установлено'}</b>" if current_media else "📎 Медиа: <b>не установлено</b>"

    await callback.message.edit_text(
        "🖼 <b>Изменение медиа подписки</b>\n\n"
        f"{status}\n\n"
        "Отправьте <b>фото</b> или <b>GIF</b>, которое будет прикреплено к сообщению о подписке.\n"
        "Или нажмите «🔙 Назад» для отмены.",
        reply_markup=admin_panel_keyboard(),
    )
    await state.set_state(AdminStates.waiting_sub_media)
    await callback.answer()


@router.message(AdminStates.waiting_sub_media, F.photo)
async def handle_new_sub_photo(message: types.Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        return

    file_id = message.photo[-1].file_id
    await set_setting("sub_media", file_id)
    await set_setting("sub_media_type", "photo")
    await state.clear()
    await message.answer(
        "✅ Фото для сообщения о подписке установлено!",
        reply_markup=admin_panel_keyboard(),
    )


@router.message(AdminStates.waiting_sub_media, F.animation)
async def handle_new_sub_gif(message: types.Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        return

    file_id = message.animation.file_id
    await set_setting("sub_media", file_id)
    await set_setting("sub_media_type", "animation")
    await state.clear()
    await message.answer(
        "✅ GIF для сообщения о подписке установлена!",
        reply_markup=admin_panel_keyboard(),
    )


# ───────── Удалить медиа подписки ─────────

@router.callback_query(F.data == "admin_delete_sub_media")
async def cb_delete_sub_media(callback: types.CallbackQuery) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    await set_setting("sub_media", "")
    await set_setting("sub_media_type", "")

    await callback.message.edit_text(
        "🗑 Медиа подписки <b>удалено</b>.\n\n"
        "Теперь сообщение о подписке будет отправляться без медиа.",
        reply_markup=admin_panel_keyboard(),
    )
    await callback.answer("Медиа удалено")
