from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base


class Feedback(Base):
    """Модель для обратной связи от пользователей"""
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    # Тип: proposal (предложение), problem (проблема), cooperation (сотрудничество)
    type: Mapped[str] = mapped_column(String(50), default="proposal")
    message: Mapped[str] = mapped_column(Text)
    
    # Статус: new, processed, archived
    status: Mapped[str] = mapped_column(String(20), default="new")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Связь с пользователем
    user: Mapped["User"] = relationship("User", back_populates="feedbacks")

# Нужно добавить relationship в модель User
