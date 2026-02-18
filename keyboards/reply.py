from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import ADMIN_ID

def main_menu_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    # Формируем кнопки
    buttons = [
        [
            KeyboardButton(text="🌐 Мой язык"),
            KeyboardButton(text="🔗 Создать инвайт")
        ],
        [
            KeyboardButton(text="❌ Завершить чат")
        ]
    ]

    # Если админ — добавляем кнопку админки
    if user_id == ADMIN_ID:
        buttons.append([KeyboardButton(text="⚙️ Админ-панель")])

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True, # Делает кнопки компактными
        input_field_placeholder="Выберите действие..."
    )