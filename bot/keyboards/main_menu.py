from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo
)
from bot.config import WEBAPP_URL


def get_main_menu() -> ReplyKeyboardMarkup:
    """Главное меню бота — 8 разделов"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🔍 Поиск"),
            ],
            [
                KeyboardButton(text="🔍 Арендовать"),
                KeyboardButton(text="🏷 Сдать оборудование"),
            ],
            [
                KeyboardButton(text="🛍 Магазин"),
                KeyboardButton(text="🎓 Обучение"),
            ],
            [
                KeyboardButton(text="📋 Мои объявления"),
                KeyboardButton(text="🚁 Мои задачи"),
            ],
            [
                KeyboardButton(text="📄 Договор ИИ"),
                KeyboardButton(text="👤 Профиль"),
            ],
            [
                KeyboardButton(text="🗺 Карта (TMA)", web_app=WebAppInfo(url=f"{WEBAPP_URL}/map")),
                KeyboardButton(text="🛍 Каталог (TMA)", web_app=WebAppInfo(url=f"{WEBAPP_URL}/webapp/catalog")),
            ],
            [
                KeyboardButton(text="🆘 ЧП"),
                KeyboardButton(text="🎬 Операторы"),
            ],
            [
                KeyboardButton(text="📩 Обратная связь"),
                KeyboardButton(text="📝 Разместить Вакансию"),
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


def get_user_type_keyboard() -> InlineKeyboardMarkup:
    """Выбор типа пользователя"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👤 Частное лицо", callback_data="user_type_private"),
                InlineKeyboardButton(text="🏢 Компания / Прокат", callback_data="user_type_company")
            ]
        ]
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()
