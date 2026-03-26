import logging
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.keyboards import get_main_menu

router = Router()
logger = logging.getLogger(__name__)

@router.message(F.text == "🆘 ЧП")
async def emergency_main(message: types.Message):
    """Главный раздел ЧП (гуманитарные миссии)"""
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🙋‍♂️ Я волонтер (готов помочь)", callback_data="chp_volunteer")],
        [InlineKeyboardButton(text="🚁 Запросить помощь дроном", callback_data="chp_request")],
        [InlineKeyboardButton(text="📍 Карта событий", callback_data="chp_map")]
    ])

    await message.answer(
        "🆘 <b>Раздел чрезвычайных ситуаций (ЧП)</b>\n\n"
        "Этот раздел предназначен для бесплатной гуманитарной помощи с использованием БПЛА.\n\n"
        "🔹 <i>Если вы готовы помочь своим дроном в поисках или мониторинге, зарегистрируйтесь как волонтер.</i>\n\n"
        "⚠️ <b>Внимание:</b> раздел не предназначен для коммерческих или военных задач.",
        parse_mode="HTML",
        reply_markup=kb
    )

@router.callback_query(F.data.startswith("view_cat:") & F.data.contains(":7:"))
async def emergency_from_catalog(callback: types.CallbackQuery):
    """Переход в ЧП из каталога"""
    await emergency_main(callback.message)
    await callback.answer()

@router.callback_query(F.data == "chp_volunteer")
async def chp_volunteer(callback: types.CallbackQuery):
    await callback.message.answer(
        "🙋‍♂️ <b>Регистрация волонтера</b>\n\n"
        "Пожалуйста, заполните небольшую анкету, чтобы мы могли связаться с вами в случае необходимости в вашем регионе.\n\n"
        "<i>(Логика регистрации в разработке)</i>",
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "chp_request")
async def chp_request(callback: types.CallbackQuery):
    await callback.message.answer(
        "🆘 <b>Запрос помощи</b>\n\n"
        "Опишите ситуацию и укажите местоположение. Ваша заявка будет отправлена ближайшим волонтерам.",
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "chp_map")
async def chp_map(callback: types.CallbackQuery):
    await callback.message.answer("📍 <b>Карта событий ЧП:</b>\n\nРаздел в разработке.", parse_mode="HTML")
    await callback.answer()
