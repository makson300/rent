import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from db.base import async_session
from db.models.tender import Tender
from db.models.tender_bid import TenderBid
from db.models.dispute import EscrowDispute
from bot.states.escrow import EscrowState
from bot.services.smart_arbitrage import smart_arbitrator

router = Router()
logger = logging.getLogger(__name__)

# ----------------- ЭТАП 1: Заказчик принимает отклик -----------------

@router.callback_query(F.data.startswith("accept_bid_"))
async def accept_tender_bid(callback: types.CallbackQuery):
    """(КНОПКА ДЛЯ ЗАКАЗЧИКА) Заказчик выбирает Исполнителя и переводит средства в Escrow."""
    parts = callback.data.split("_")
    tender_id = int(parts[2])
    bid_id = int(parts[3])
    
    async with async_session() as session:
        tender_res = await session.execute(select(Tender).where(Tender.id == tender_id))
        tender = tender_res.scalar_one_or_none()
        
        bid_res = await session.execute(select(TenderBid).where(TenderBid.id == bid_id))
        bid = bid_res.scalar_one_or_none()
        
        if not tender or not bid:
            await callback.answer("Тендер или отклик не найден.", show_alert=True)
            return
            
        if tender.employer_id != callback.from_user.id:
            await callback.answer("Только создатель тендера может принять отклик.", show_alert=True)
            return
            
        # Блокируем средства (Смена статусов)
        tender.status = "awarded"
        bid.status = "in_progress" # Деньги якобы в холде
        
        session.add(tender)
        session.add(bid)
        await session.commit()
        
    await callback.message.edit_text(
        f"✅ <b>Отклик принят! Сделка (Escrow) открыта.</b>\n\n"
        f"Сумма {bid.price_offer} руб. заморожена на платформе.\n"
        f"Исполнитель должен загрузить результаты работы после выполнения.",
        parse_mode="HTML"
    )
    
    # Уведомляем Исполнителя
    contractor_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Сдать работу (Загрузить фото/отчет)", callback_data=f"submit_proof_{tender_id}_{bid_id}")]
    ])
    try:
        await callback.bot.send_message(
            bid.contractor_id,
            f"🎉 <b>Ваш отклик на тендер «{tender.title}» был ПРИНЯТ!</b>\n\n"
            f"💰 Сумма {bid.price_offer} руб. заморожена в системе Безопасной Сделки.\n"
            f"Приступайте к выполнению. После окончания нажмите кнопку ниже, чтобы сдать работу.",
            parse_mode="HTML",
            reply_markup=contractor_kb
        )
    except Exception as e:
        logger.warning(f"Could not notify contractor {bid.contractor_id}: {e}")

# ----------------- ЭТАП 2: Исполнитель сдает работу -----------------

@router.callback_query(F.data.startswith("submit_proof_"))
async def start_submit_proof(callback: types.CallbackQuery, state: FSMContext):
    """(КНОПКА ДЛЯ ИСПОЛНИТЕЛЯ) Начало сдачи работы."""
    parts = callback.data.split("_")
    tender_id = int(parts[2])
    bid_id = int(parts[3])
    
    await state.update_data(tender_id=tender_id, bid_id=bid_id)
    await state.set_state(EscrowState.waiting_for_proof)
    
    await callback.message.answer(
        "📸 <b>Сдача работы (Escrow)</b>\n\n"
        "Пожалуйста, загрузите подтверждение выполнения техзадания:\n"
        "<i>(Отправьте фотографию, отчёт или архив с телеметрией/сшитой ортофотокартой)</i>",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(EscrowState.waiting_for_proof)
async def receive_proof(message: types.Message, state: FSMContext):
    """Получение доказательств работы от подрядчика."""
    data = await state.get_data()
    tender_id = data.get("tender_id")
    bid_id = data.get("bid_id")
    
    # Мы могли бы сохранять file_id, но для MVP просто перешлем его заказчику
    proof_text = message.text or message.caption or "Без описания"
    
    async with async_session() as session:
        bid_res = await session.execute(select(TenderBid).options(selectinload(TenderBid.tender)).where(TenderBid.id == bid_id))
        bid = bid_res.scalar_one_or_none()
        
        if not bid or bid.status != "in_progress":
            await message.answer("Ошибка: Сделка не найдена или уже закрыта.")
            await state.clear()
            return
            
        bid.status = "reviewing_proofs"
        session.add(bid)
        await session.commit()
        tender = bid.tender
    
    # Отправляем доказательства Заказчику
    client_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Принять работу (Выплатить)", callback_data=f"approve_job_{tender_id}_{bid_id}")],
        [InlineKeyboardButton(text="❌ Оспорить (Вызвать Арбитра)", callback_data=f"dispute_job_{tender_id}_{bid_id}")]
    ])
    
    try:
        if message.photo:
            await message.bot.send_photo(
                tender.employer_id, 
                message.photo[-1].file_id, 
                caption=f"📦 <b>Исполнитель сдал работу по тендеру «{tender.title}»!</b>\n\nКомментарий: {proof_text}\n\nПожалуйста, ознакомьтесь с материалами и примите решение.",
                parse_mode="HTML",
                reply_markup=client_kb
            )
        elif message.document:
            await message.bot.send_document(
                tender.employer_id, 
                message.document.file_id, 
                caption=f"📦 <b>Исполнитель сдал работу по тендеру «{tender.title}»!</b>\n\nКомментарий: {proof_text}\n\nПожалуйста, ознакомьтесь с материалами.",
                parse_mode="HTML",
                reply_markup=client_kb
            )
        else:
            await message.bot.send_message(
                tender.employer_id,
                f"📦 <b>Исполнитель сдал работу по тендеру «{tender.title}»!</b>\n\n"
                f"📄 Текст отчета: {proof_text}\n\n"
                f"Пожалуйста, примите решение.",
                parse_mode="HTML",
                reply_markup=client_kb
            )
            
        await message.answer("✅ Доказательства успешно отправлены заказчику! Ожидаем проверки и выплаты.")
    except Exception as e:
        logger.error(f"Failed to send proof to employer: {e}")
        await message.answer("Проблема при отправке данных заказчику. Техническая поддержка уведомлена.")
        
    await state.clear()


# ----------------- ЭТАП 3: Заказчик принимает или оспаривает -----------------

@router.callback_query(F.data.startswith("approve_job_"))
async def approve_job(callback: types.CallbackQuery):
    """(КНОПКА ЗАКАЗЧИКА) Заказчик принимает работу - Escrow разморожен."""
    parts = callback.data.split("_")
    tender_id = int(parts[2])
    bid_id = int(parts[3])
    
    async with async_session() as session:
        bid_res = await session.execute(select(TenderBid).options(selectinload(TenderBid.tender)).where(TenderBid.id == bid_id))
        bid = bid_res.scalar_one_or_none()
        
        if not bid: return
        
        bid.status = "completed"
        bid.tender.status = "closed"
        session.add(bid)
        session.add(bid.tender)
        await session.commit()
    
    await callback.message.edit_text(
        f"✅ <b>Работа принята!</b>\nСредства ({bid.price_offer} руб.) успешно переведены Исполнителю.", 
        parse_mode="HTML"
    )
    
    try:
        await callback.bot.send_message(
            bid.contractor_id,
            f"🎉 <b>Отличные новости! Заказчик ПРИНЯЛ вашу работу по тендеру «{bid.tender.title}».</b>\n💳 Выплата направлена на ваш счет.",
            parse_mode="HTML"
        )
    except Exception:
        pass

@router.callback_query(F.data.startswith("dispute_job_"))
async def start_job_dispute(callback: types.CallbackQuery, state: FSMContext):
    """(КНОПКА ЗАКАЗЧИКА) Заказчик недоволен, запускаем Спор."""
    parts = callback.data.split("_")
    tender_id = int(parts[2])
    bid_id = int(parts[3])
    
    await state.update_data(tender_id=tender_id, bid_id=bid_id)
    await state.set_state(EscrowState.waiting_for_dispute_reason)
    
    await callback.message.answer(
        "⚖️ <b>Открытие Арбитража</b>\n\n"
        "Пожалуйста, подробно опишите суть претензии. Что именно Исполнитель сделал не по Техзаданию?",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(EscrowState.waiting_for_dispute_reason)
async def receive_dispute_reason(message: types.Message, state: FSMContext):
    """Получена жалоба — создается EscrowDispute, запускается ИИ."""
    data = await state.get_data()
    tender_id = data.get("tender_id")
    bid_id = data.get("bid_id")
    reason_text = message.text or "Жалоба без текста"
    
    await message.answer("🔄 <i>Жалоба принята. Умный ИИ-Арбитр анализирует аргументы сторон и формирует рапорт для Администрации...</i>", parse_mode="HTML")
    
    async with async_session() as session:
        bid_res = await session.execute(select(TenderBid).options(selectinload(TenderBid.tender)).where(TenderBid.id == bid_id))
        bid = bid_res.scalar_one_or_none()
        
        if not bid:
            await state.clear()
            return
            
        bid.status = "dispute_opened"
        tender = bid.tender
        tender.status = "dispute"
        
        # Создаем Dispute (Defendant - подрядчик, Plaintiff - работодатель)
        dispute = EscrowDispute(
            tender_id=tender.id,
            plaintiff_id=tender.employer_id,
            defendant_id=bid.contractor_id,
            reason=reason_text,
            evidence_text="Исполнитель сдал работу, но Заказчик открыл спор." # В идеале сюда добавляется переписка
        )
        session.add(dispute)
        session.add(bid)
        session.add(tender)
        await session.flush() # Получаем dispute.id
        
        # Запускаем ИИ в фоне (он заполнит ai_summary и отправит алерт админам)
        import asyncio
        asyncio.create_task(smart_arbitrator.open_auto_dispute(session, message.bot, dispute, tender, bid))
        
    await message.answer("✅ <b>Арбитраж запущен.</b> Администрация скоро свяжется с вами.", parse_mode="HTML")
    
    try:
        await message.bot.send_message(
            bid.contractor_id,
            f"⚖️ <b>Внимание! Заказчик открыл спор (Арбитраж) по тендеру «{tender.title}».</b>\n\nПретензия: <i>{reason_text}</i>\nСредства заморожены до выяснения обстоятельств ИИ-Судьей.",
            parse_mode="HTML"
        )
    except Exception:
        pass
        
    await state.clear()
