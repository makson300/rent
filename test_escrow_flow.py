import asyncio
from db.base import async_session, Base
from db.models.user import User
from db.models.tender import Tender
from db.models.tender_bid import TenderBid
from db.models.dispute import EscrowDispute
try:
    from db.models.reward import Reward
except ImportError:
    pass
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_escrow")

async def run_test():
    logger.info("Начало тестирования базы Escrow...")
    
    async with async_session() as session:
        # Для обхода проблемы constraint-ов User в SQLite для локального тестирования, 
        # используем несуществующие или уже существующие ID без INSERT INTO users
        employer_id = 9001
        contractor_id = 9002
        
        from datetime import datetime, timedelta
        # Создаем тендер
        tender = Tender(
            employer_id=9001,
            title="Тестовый тендер",
            description="Съемка стройки",
            category="photo",
            region="Москва",
            budget=50000,
            deadline=datetime.utcnow() + timedelta(days=5),
            status="active"
        )
        session.add(tender)
        await session.flush()
        
        # Создаем отклик
        bid = TenderBid(
            tender_id=tender.id,
            contractor_id=9002,
            price_offer=45000,
            comment="Готов выполнить",
            status="in_progress"
        )
        session.add(bid)
        await session.flush()
        
        # Симулируем открытие спора
        tender.status = "dispute"
        dispute = EscrowDispute(
            tender_id=tender.id,
            plaintiff_id=9001, # заказчик
            defendant_id=9002, # исполнитель
            reason="Некачественные фото",
            status="open"
        )
        session.add(dispute)
        await session.commit()
        
        # Чтение и верификация связей
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        res = await session.execute(
            select(EscrowDispute)
            .where(EscrowDispute.tender_id == tender.id)
        )
        fetched_dispute = res.scalar_one_or_none()
        
        if fetched_dispute:
            logger.info("✅ УСПЕХ: Спор успешно записан и связан с тендером!")
            logger.info(f"Спор ID: {fetched_dispute.id}, Причина: {fetched_dispute.reason}")
        else:
            logger.error("❌ ОШИБКА: Спор не найден в БД!")
            
        # Очистка (Rollback / Delete)
        await session.delete(fetched_dispute)
        await session.delete(bid)
        await session.delete(tender)
        await session.commit()
        logger.info("✅ Очистка завершена.")

if __name__ == "__main__":
    asyncio.run(run_test())
