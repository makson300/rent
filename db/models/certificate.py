from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from db.base import Base

class PilotCertificate(Base):
    __tablename__ = "pilot_certificates"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"), nullable=False)
    cert_type = Column(String(255), nullable=False) # e.g. "Агродроны", "БВС до 30 кг"
    document_number = Column(String(100), nullable=True) # Росавиация / Госуслуги реестр
    issue_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    is_verified = Column(Boolean, default=False) # Verified via Gosuslugi integration
    
    created_at = Column(DateTime, default=datetime.utcnow)
