from sqlalchemy import Column, Integer, BigInteger, ForeignKey, DateTime
from datetime import datetime
from db.base import Base

class JobResponse(Base):
    __tablename__ = "job_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    pilot_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
