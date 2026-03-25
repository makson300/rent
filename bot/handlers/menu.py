from aiogram import Router, types, F
from bot.keyboards import get_main_menu

router = Router()


@router.message(F.text == "🔍 Арендовать")
async def rental_menu(message: types.Message):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from bot.handlers.listing_create import CITIES
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=city, callback_data=f"view_city_{city}")] for city in CITIES
    ])
    
    await message.answer(
        "🔍 <b>Раздел «Аренда»</b>\n\n"
        "Выберите город из списка ниже 🏙",
        parse_mode="HTML",
        reply_markup=kb,
    )


@router.message(F.text == "🏷 Сдать оборудование")
async def rent_out_menu(message: types.Message):
    """Вывод правил и пакетов размещения для ЮKassa"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    text = (
        "🏷 <b>Размещение оборудования</b>\n\n"
        "Перед размещением ознакомьтесь с нашими тарифами на услуги публикации объявлений.\n\n"
        "<b>Пакеты (1 объявление):</b>\n"
        "🔹 1 месяц — 700 ₽\n"
        "🔹 6 месяцев — 2 500 ₽\n"
        "🔹 12 месяцев — 3 500 ₽\n\n"
        "<b>Пакеты (5 объявлений):</b>\n"
        "🔹 1 месяц суммарно — 2 500 ₽\n"
        "🔹 6 месяцев суммарно — 7 000 ₽\n"
        "🔹 12 месяцев суммарно — 9 000 ₽\n\n"
        "<i>Для продолжения публикации необходимо выбрать пакет и оплатить размещение.</i>"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить (Тест) и продолжить", callback_data="start_listing_create")]
    ])
    await message.answer(text, parse_mode="HTML", reply_markup=kb)


@router.message(F.text.in_({"🆘 ЧП", "🎧 Поддержка"}))
async def stub_menu(message: types.Message):
    """Заглушки для новых кнопок"""
    await message.answer(
        f"🚧 Раздел <b>«{message.text.strip('🎓🆘📜🎧 ')}»</b> находится в разработке.",
        parse_mode="HTML",
        reply_markup=get_main_menu(),
    )
