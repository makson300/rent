from sqlalchemy import Column, Integer, String, Text, BigInteger, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from db.base import Base

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    employer_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=True) # Допускается NULL для вакансий с hh.ru
    pilot_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=True) # Пилот-исполнитель
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    city = Column(String(100), nullable=False)
    budget = Column(String(100), nullable=False)
    
    lat = Column(Float, nullable=True)    
    lng = Column(Float, nullable=True)
    
    status = Column(String(20), default="pending") # pending, active, closed, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    
    source_url = Column(String(500), nullable=True) # Ссылка на внешний ресурс (hh.ru)
    external_id = Column(String(100), nullable=True, unique=True) # ID вакансии (для защиты от дублей)
    clicks_count = Column(Integer, default=0) # Аналитика: количество кликов по вакансии
    
    employer = relationship("User", foreign_keys=[employer_id])
