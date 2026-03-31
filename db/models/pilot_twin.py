from datetime import datetime
from sqlalchemy import BigInteger, ForeignKey, Float, Integer, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base

class PilotTwin(Base):
    __tablename__ = "pilot_twins"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    
    # Ключевые метрики
    total_flight_hours: Mapped[float] = mapped_column(Float, default=0.0)
    total_missions: Mapped[int] = mapped_column(Integer, default=0)
    
    # B2G Рейтинги (0 - 100)
    safety_score: Mapped[float] = mapped_column(Float, default=100.0)
    success_rate: Mapped[float] = mapped_column(Float, default=100.0)
    
    # AI Оценка (MoMoA Grade)
    momoa_grade: Mapped[str] = mapped_column(String(10), default="A")
    skills_json: Mapped[str | None] = mapped_column(Text, nullable=True) # ['RTK', 'Лидар']
    
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связи
    user = relationship("User", back_populates="twin")
