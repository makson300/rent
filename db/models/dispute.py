from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from db.base import Base

class EscrowDispute(Base):
    __tablename__ = "escrow_disputes"
    
    id = Column(Integer, primary_key=True)
    tender_id = Column(Integer, ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False)
    plaintiff_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=False) # Кто открыл спор
    defendant_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=False) # На кого жалуются
    reason = Column(Text, nullable=False) # Первичная жалоба
    evidence_text = Column(Text, nullable=True) # Переписка/аргументы
    ai_summary = Column(Text, nullable=True) # Рекомендация ИИ (AI Judge)
    status = Column(String(50), default="open") # open, ai_reviewed, closed_paid, closed_refunded
    
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
