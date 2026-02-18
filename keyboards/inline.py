from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import LANGUAGES, ADMIN_ID


def language_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора языка (по 3 кнопки в ряд)."""
    buttons: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for code, name in LANGUAGES.items():
        row.append(InlineKeyboardButton(
            text=name,
            callback_data=f"set_lang:{code}",
        ))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def main_menu_keyboard(user_id: int | None = None) -> InlineKeyboardMarkup:
    """Главная клавиатура бота."""
    buttons = [
        [
            InlineKeyboardButton(text="🌐 Мой язык", callback_data="my_lang"),
            InlineKeyboardButton(text="🔗 Создать инвайт", callback_data="create_invite"),
        ],
        [
            InlineKeyboardButton(text="❌ Завершить чат", callback_data="end_chat"),
        ],
    ]
    if user_id == ADMIN_ID:
        buttons.append([
            InlineKeyboardButton(text="⚙️ Админ-панель", callback_data="admin_panel"),
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_panel_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура админ-панели."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="✏️ Изменить текст подписки", callback_data="admin_edit_sub_text")],
        [InlineKeyboardButton(text="🖼 Изменить медиа подписки", callback_data="admin_edit_sub_media")],
        [InlineKeyboardButton(text="🗑 Удалить медиа подписки", callback_data="admin_delete_sub_media")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")],
    ])
