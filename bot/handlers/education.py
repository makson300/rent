import logging
from aiogram import Router, types, F
from bot.keyboards import get_main_menu
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()
logger = logging.getLogger(__name__)

# --- ОБУЧЕНИЕ ---

@router.message(F.text == "🎓 Обучение")
async def education_main(message: types.Message):
    """Главный экран раздела Обучение"""
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 База знаний", callback_data="edu_base")],
        [InlineKeyboardButton(text="💼 Обучение профессии", callback_data="edu_pro")],
        [InlineKeyboardButton(text="👶 Для детей (Offline MSK)", callback_data="edu_kids")]
    ])
    await message.answer(
        "🎓 <b>Раздел обучения</b>\n\n"
        "Выберите интересующее вас направление:",
        parse_mode="HTML",
        reply_markup=kb
    )

@router.callback_query(F.data == "edu_base")
async def edu_base(callback: types.CallbackQuery):
    await callback.message.answer(
        "📚 <b>База знаний</b>\n\n"
        "Здесь собраны полезные статьи, чек-листы и инструкции по работе с оборудованием.\n\n"
        "<i>Раздел наполняется контентом...</i>",
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "edu_pro")
async def edu_pro(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚜 Агродроны", callback_data="edu_pro_agro")],
        [InlineKeyboardButton(text="🏗 Промышленные дроны", callback_data="edu_pro_ind")],
        [InlineKeyboardButton(text="📸 Профессиональная съемка", callback_data="edu_pro_photo")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="edu_back")]
    ])
    await callback.message.edit_text(
        "💼 <b>Обучение профессии</b>\n\n"
        "Выберите направление подготовки специалистов:",
        parse_mode="HTML",
        reply_markup=kb
    )
    await callback.answer()

@router.callback_query(F.data == "edu_kids")
async def edu_kids(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Подать заявку", url="https://t.me/VMANDCO")], # Placeholder link to admin
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="edu_back")]
    ])
    await callback.message.edit_text(
        "👶 <b>Обучение для детей</b>\n\n"
        "📍 Формат: Офлайн (Москва)\n"
        "👥 Возраст: от 8 до 16 лет\n\n"
        "Интересные занятия по пилотированию и основам робототехники под руководством опытных инструкторов.\n\n"
        "Нажмите кнопку ниже, чтобы подать заявку!",
        parse_mode="HTML",
        reply_markup=kb
    )
    await callback.answer()

@router.callback_query(F.data == "edu_back")
async def edu_back(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 База знаний", callback_data="edu_base")],
        [InlineKeyboardButton(text="💼 Обучение профессии", callback_data="edu_pro")],
        [InlineKeyboardButton(text="👶 Для детей (Offline MSK)", callback_data="edu_kids")]
    ])
    await callback.message.edit_text(
        "🎓 <b>Раздел обучения</b>\n\n"
        "Выберите интересующее вас направление:",
        parse_mode="HTML",
        reply_markup=kb
    )
    await callback.answer()

# --- ПРАВИЛА ---

@router.message(F.text == "📜 Правила и условия")
async def rules_main(message: types.Message):
    """Раздел Правил и рекомендаций"""
    text = (
        "📜 <b>Правила и рекомендации</b>\n\n"
        "⚠️ <b>Отказ от ответственности:</b>\n"
        "Наш бот является информационным ресурсом (доской объявлений). "
        "Мы берем плату исключительно за услуги размещения объявлений. "
        "<b>Мы не являемся стороной сделки и не несем ответственности за действия пользователей.</b>\n\n"
        "💡 <b>Рекомендации:</b>\n\n"
        "👤 <b>Для тех, кто сдает:</b>\n"
        "• Всегда проверяйте документы арендатора.\n"
        "• Составляйте акт приема-передачи оборудования.\n"
        "• Берите залог (денежный или паспортный, если это законно в вашем регионе).\n"
        "• Снимайте видео работы оборудования при выдаче.\n\n"
        "🔍 <b>Для тех, кто арендует:</b>\n"
        "• Проверяйте оборудование при получении.\n"
        "• Уточняйте условия ответственности при поломке.\n"
        "• Не переводите предоплату незнакомым лицам без гарантий."
    )
    await message.answer(text, parse_mode="HTML", reply_markup=get_main_menu())
