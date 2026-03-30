from sqlalchemy import Column, Integer, String, Text, BigInteger, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from db.base import Base

class TenderBid(Base):
    __tablename__ = "tender_bids"
    
    id = Column(Integer, primary_key=True)
    tender_id = Column(Integer, ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False)
    contractor_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    price_offer = Column(Integer, nullable=False) # Предложенная цена
    comment = Column(Text, nullable=True) # Описание услуг/сроков, контактные данные
    status = Column(String(50), default="pending") # pending, accepted, rejected, rejected_by_ai
    ai_reason = Column(Text, nullable=True) # Причина блокировки от ИИ
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Опционально: связь с тендером
    # tender = relationship("Tender", back_populates="bids")
