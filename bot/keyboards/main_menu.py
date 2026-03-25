from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)


def get_main_menu() -> ReplyKeyboardMarkup:
    """Главное меню бота — 8 разделов"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🔍 Арендовать"),
                KeyboardButton(text="🏷 Сдать оборудование"),
            ],
            [
                KeyboardButton(text="🎓 Обучение"),
                KeyboardButton(text="🆘 ЧП"),
            ],
            [
                KeyboardButton(text="📋 Мои объявления"),
                KeyboardButton(text="👤 Профиль"),
            ],
            [
                KeyboardButton(text="📜 Правила и условия"),
                KeyboardButton(text="🎧 Поддержка"),
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
