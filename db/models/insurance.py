from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from db.base import Base

class InsurancePolicy(Base):
    __tablename__ = "insurance_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=False, index=True)
    drone_model = Column(String(100), nullable=False)
    serial_number = Column(String(100), nullable=False)
    coverage_amount = Column(Float, nullable=False) # На какую сумму застрахован
    premium = Column(Float, nullable=False) # Сколько уплачено
    status = Column(String(50), default="active") # active, expired, cancelled
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=False) # Обычно +30 дней
    
    user = relationship("User")
