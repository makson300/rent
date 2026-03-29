from sqlalchemy import Column, Integer, String, Text, BigInteger, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from db.base import Base

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    employer_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    city = Column(String(100), nullable=False)
    budget = Column(String(100), nullable=False)
    status = Column(String(20), default="pending") # pending, active, closed, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    
    employer = relationship("User", foreign_keys=[employer_id])
