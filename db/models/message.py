from sqlalchemy import Column, Integer, Text, Boolean, BigInteger, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from db.base import Base

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=False, index=True)
    receiver_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=False, index=True)
    
    # Привязываем чат к сделке (Тендеру) - обязательно или нет (может просто p2p)
    tender_id = Column(Integer, ForeignKey("tenders.id", ondelete="CASCADE"), nullable=True)
    
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
