from aiogram import Router, types, F
from bot.keyboards import get_main_menu

router = Router()


@router.message(F.text == "🏠 Аренда")
async def rental_menu(message: types.Message):
    """Заглушка раздела аренды — будет реализован на Этапе 3"""
    await message.answer(
        "🏠 <b>Раздел «Аренда»</b>\n\n"
        "🚧 Раздел в разработке. Скоро здесь появится каталог оборудования!",
        parse_mode="HTML",
        reply_markup=get_main_menu(),
    )


@router.message(F.text == "🎓 Обучение")
async def education_menu(message: types.Message):
    """Заглушка раздела обучения — будет реализован на Этапе 4"""
    await message.answer(
        "🎓 <b>Раздел «Обучение»</b>\n\n"
        "🚧 Раздел в разработке. Скоро здесь будут курсы и PDF-материалы!",
        parse_mode="HTML",
        reply_markup=get_main_menu(),
    )


@router.message(F.text == "🆘 ЧП / События")
async def chp_menu(message: types.Message):
    """Заглушка раздела ЧП — будет реализован на Этапе 5"""
    await message.answer(
        "🆘 <b>Раздел «ЧП / События»</b>\n\n"
        "🚧 Раздел в разработке. Скоро здесь можно будет размещать ЧП-объявления!",
        parse_mode="HTML",
        reply_markup=get_main_menu(),
    )
