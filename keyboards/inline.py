from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import LANGUAGES, CHANNEL_URL

def language_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for code, name in LANGUAGES.items():
        row.append(InlineKeyboardButton(text=name, callback_data=f"set_lang:{code}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def admin_panel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        # 👇 Новая кнопка
        [InlineKeyboardButton(text="👁 Просмотреть сообщение", callback_data="admin_preview_sub")],
        [InlineKeyboardButton(text="✏️ Изменить текст подписки", callback_data="admin_edit_sub_text")],
        [InlineKeyboardButton(text="🖼 Изменить медиа подписки", callback_data="admin_edit_sub_media")],
        [InlineKeyboardButton(text="🗑 Удалить медиа подписки", callback_data="admin_delete_sub_media")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")],
    ])

# Клавиатура под постом подписки (для пользователей)
def subscribe_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Подписаться", url=CHANNEL_URL)],
        [InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_sub")],
    ])

# Клавиатура для предпросмотра (для админа)
def admin_preview_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Подписаться (тест)", url=CHANNEL_URL)],
        [InlineKeyboardButton(text="✅ Проверить подписку (тест)", callback_data="check_sub")],
        # Кнопка возврата в админку
        [InlineKeyboardButton(text="🔙 В админ-панель", callback_data="admin_panel")]
    ])