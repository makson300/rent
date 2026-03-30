from sqlalchemy import Column, Integer, String, Text, BigInteger, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from db.base import Base

class Tender(Base):
    __tablename__ = "tenders"
    
    id = Column(Integer, primary_key=True, index=True)
    employer_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    budget = Column(Integer, nullable=False) # Начальная Максимальная Цена Контракта (НМЦК)
    deadline = Column(DateTime, nullable=False)
    status = Column(String(50), default="active") # active, closed, awarded, cancelled
    region = Column(String(150), nullable=False)
    lat = Column(Float, nullable=True) # Гео-координаты для Радара Тендеров
    lng = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Опционально: связь с откликами
    # bids = relationship("TenderBid", back_populates="tender", cascade="all, delete-orphan")
