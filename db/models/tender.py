from sqlalchemy import Column, Integer, String, Text, BigInteger, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from db.base import Base

class Tender(Base):
    __tablename__ = "tenders"
    
    id = Column(Integer, primary_key=True, index=True)
    employer_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=True) # nullable for B2G
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
    
    # B2G Specific properties
    is_b2g = Column(Boolean, default=False)
    is_vip = Column(Boolean, default=False)
    b2g_status = Column(String(50), default="new") # new, approved, rejected
    eis_fz = Column(String(50), nullable=True) # 44-ФЗ, 223-ФЗ
    customer_name = Column(String(255), nullable=True) # Наименование заказчика
    b2g_url = Column(String(500), nullable=True) # Ссылка на ЕИС
    
    # Опционально: связь с откликами
    bids = relationship("TenderBid", back_populates="tender", cascade="all, delete-orphan")
