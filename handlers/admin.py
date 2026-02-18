from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_ID
from db import get_total_users, get_active_chats, get_setting, set_setting
# 👇 Добавили admin_preview_keyboard
from keyboards.inline import admin_panel_keyboard, admin_preview_keyboard
from keyboards.reply import main_menu_keyboard

router = Router()


class AdminStates(StatesGroup):
    waiting_sub_text = State()
    waiting_sub_media = State()


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


# 👇 Ловим кнопку с нижнего меню "⚙️ Админ-панель"
@router.message(F.text == "⚙️ Админ-панель")
async def cmd_admin_panel(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    await message.answer("⚙️ <b>Админ-панель</b>\n\nВыберите действие:", reply_markup=admin_panel_keyboard())


# Кнопка "Назад" возвращает к основному сообщению админки
@router.callback_query(F.data == "admin_panel")
async def cb_back_to_main(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id): return
    await state.clear()

    # Если мы вернулись из режима просмотра (где было фото), лучше отправить новое сообщение
    # а старое (с фото) можно удалить или оставить. Для простоты - редактируем текст если можно, или шлем новое.
    try:
        await callback.message.edit_text("⚙️ <b>Админ-панель</b>", reply_markup=admin_panel_keyboard())
    except:
        # Если нельзя отредактировать (например, было фото, а стало текст), шлем новое
        await callback.message.delete()
        await callback.message.answer("⚙️ <b>Админ-панель</b>", reply_markup=admin_panel_keyboard())


@router.callback_query(F.data == "admin_back")
async def cb_admin_exit(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id): return
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("🏠 Вы вышли из админки", reply_markup=main_menu_keyboard(callback.from_user.id))


# --- Логика предпросмотра ---
@router.callback_query(F.data == "admin_preview_sub")
async def cb_admin_preview(callback: CallbackQuery):
    if not is_admin(callback.from_user.id): return

    sub_text = await get_setting("sub_text")
    sub_media = await get_setting("sub_media")
    sub_media_type = await get_setting("sub_media_type")

    # Удаляем меню админки, чтобы показать превью "чисто"
    await callback.message.delete()

    kb = admin_preview_keyboard()  # Клавиатура с кнопкой "Назад в админку"

    if sub_media and sub_media_type:
        try:
            if sub_media_type == "photo":
                await callback.message.answer_photo(photo=sub_media, caption=sub_text, reply_markup=kb)
            elif sub_media_type == "animation":
                await callback.message.answer_animation(animation=sub_media, caption=sub_text, reply_markup=kb)
        except Exception as e:
            await callback.message.answer(f"⚠️ Ошибка медиа: {e}\n\n{sub_text}", reply_markup=kb)
    else:
        await callback.message.answer(text=sub_text, reply_markup=kb)

    await callback.answer()


# --- Остальные хендлеры (статистика, изменение текста) остаются такими же ---
# (Я скопировал их для полноты картины, чтобы вы могли заменить файл целиком)

@router.callback_query(F.data == "admin_stats")
async def cb_admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id): return
    total_users = await get_total_users()
    active_chats = await get_active_chats()
    await callback.message.edit_text(
        f"📊 <b>Статистика бота</b>\n\n👥 Всего пользователей: <b>{total_users}</b>\n💬 Активных чатов: <b>{active_chats}</b>",
        reply_markup=admin_panel_keyboard()
    )


@router.callback_query(F.data == "admin_edit_sub_text")
async def cb_edit_sub_text(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id): return
    current_text = await get_setting("sub_text")
    await callback.message.edit_text(
        f"✏️ <b>Изменение текста подписки</b>\n\nТекущий текст:\n<blockquote>{current_text}</blockquote>\n\nОтправьте новый текст.",
        reply_markup=admin_panel_keyboard()
    )
    await state.set_state(AdminStates.waiting_sub_text)


@router.message(AdminStates.waiting_sub_text, F.text)
async def handle_new_sub_text(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    await set_setting("sub_text", message.text)
    await state.clear()
    await message.answer(
        f"✅ Текст обновлён!\n\n<blockquote>{message.text}</blockquote>",
        reply_markup=admin_panel_keyboard()
    )


@router.callback_query(F.data == "admin_edit_sub_media")
async def cb_edit_sub_media(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id): return
    current_media = await get_setting("sub_media")
    status = "Есть медиа" if current_media else "Нет медиа"
    await callback.message.edit_text(
        f"🖼 <b>Изменение медиа</b>\n\nСтатус: {status}\n\nОтправьте <b>фото</b> или <b>GIF</b>.",
        reply_markup=admin_panel_keyboard()
    )
    await state.set_state(AdminStates.waiting_sub_media)


@router.message(AdminStates.waiting_sub_media, F.photo)
async def handle_new_sub_photo(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    file_id = message.photo[-1].file_id
    await set_setting("sub_media", file_id)
    await set_setting("sub_media_type", "photo")
    await state.clear()
    await message.answer("✅ Фото установлено!", reply_markup=admin_panel_keyboard())


@router.message(AdminStates.waiting_sub_media, F.animation)
async def handle_new_sub_gif(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    file_id = message.animation.file_id
    await set_setting("sub_media", file_id)
    await set_setting("sub_media_type", "animation")
    await state.clear()
    await message.answer("✅ GIF установлена!", reply_markup=admin_panel_keyboard())


@router.callback_query(F.data == "admin_delete_sub_media")
async def cb_delete_sub_media(callback: CallbackQuery):
    if not is_admin(callback.from_user.id): return
    await set_setting("sub_media", "")
    await set_setting("sub_media_type", "")
    await callback.message.edit_text("🗑 Медиа удалено.", reply_markup=admin_panel_keyboard())