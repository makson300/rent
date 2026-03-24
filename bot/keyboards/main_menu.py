from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)


def get_main_menu() -> ReplyKeyboardMarkup:
    """Главное меню бота — 4 раздела"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🏠 Аренда"),
                KeyboardButton(text="🎓 Обучение"),
            ],
            [
                KeyboardButton(text="🆘 ЧП / События"),
                KeyboardButton(text="👤 Профиль"),
            ],
        ],
        resize_keyboard=True,
    )


def get_contact_keyboard() -> ReplyKeyboardMarkup:
    """Кнопка для отправки контакта (регистрация)"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Поделиться контактом", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()
