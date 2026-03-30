import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from db.base import async_session
from bot.services.tender_matcher import create_b2b_proposal

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("demo_tender"))
async def demo_tender_handler(message: types.Message):
    """Демонстрация работы ИИ-движка Smart Procurement."""
    wait_msg = await message.answer(
        "⏳ <b>ИИ «Горизонт» анализирует базу B2B...</b>\n\n"
        "<i>Ищем подходящее оборудование (БПЛА, тепловизоры) под ваш тендерный запрос 'Мониторинг газопроводов Сибири' и формируем отчет...</i>",
        parse_mode="HTML"
    )
    
    tender_title = "Мониторинг газопроводов Сибири"
    tender_desc = "Закупка услуг/оборудования БПЛА для проведения аэромониторинга 200км трубопровода в условиях низких температур. Нужны дроны с тепловизорами и защитой от обледенения."
    
    async with async_session() as session:
        result_msg, file_io = await create_b2b_proposal(session, tender_title, tender_desc)
        
    await wait_msg.delete()
    
    if file_io:
        await message.answer_document(
            types.BufferedInputFile(file_io.getvalue(), filename=file_io.name),
            caption=result_msg
        )
    else:
        await message.answer(result_msg)

@router.message(Command("test_b2g"))
async def test_b2g_tenders(message: types.Message):
    """Триггер парсинга и рассылки B2G тендеров."""
    wait_msg = await message.answer(
        "⏳ <b>Анализ ЕИС Закупки (Госзакупки)...</b>\n"
        "<i>MoMoA парсит техзадания текущих тендеров по аэрофотосъемке...</i>",
        parse_mode="HTML"
    )
    from bot.services.smart_tenders import run_b2g_matching
    
    # In a real app we'd spawn a background task. Since it's a test:
    matched = await run_b2g_matching(message.bot)
    
    await wait_msg.edit_text(
        f"✅ <b>B2G Матчинг завершен!</b>\n\n"
        f"Разослано PUSH-уведомлений пилотам с подходящим оборудованием: <b>{matched} шт.</b>",
        parse_mode="HTML"
    )

@router.callback_query(F.data == "tender_mock_apply")
async def tender_apply_mock(callback: types.CallbackQuery):
    await callback.message.answer("📝 Заявка оформлена. Скоро с вами свяжется менеджер B2B продаж для помощи в торгах.")
    await callback.answer()
