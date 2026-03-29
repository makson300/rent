from datetime import datetime
from sqlalchemy import Integer, String, Text, ForeignKey, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base

class EmergencyAlert(Base):
    __tablename__ = "emergency_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    reporter_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    city: Mapped[str] = mapped_column(String(100), nullable=True)
    problem_type: Mapped[str] = mapped_column(String(255), nullable=True)
    required_equipment: Mapped[str] = mapped_column(String(255), nullable=True)
    
    raw_text: Mapped[str] = mapped_column(Text)
    ai_summary: Mapped[str] = mapped_column(Text, nullable=True)
    
    lat: Mapped[float] = mapped_column(Float, nullable=True)
    lng: Mapped[float] = mapped_column(Float, nullable=True)
    
    status: Mapped[str] = mapped_column(String(50), default="pending") # pending, approved, rejected
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Реляция с репортером
    reporter = relationship("User", foreign_keys=[reporter_id])
    
