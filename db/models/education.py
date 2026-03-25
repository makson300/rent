from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base
import enum

class ApplicationStatus(enum.Enum):
    NEW = "new"
    PROCESSED = "processed"
    REJECTED = "rejected"

class EducationApplication(Base):
    """Заявки на обучение (дети)"""
    __tablename__ = "education_applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer) # Telegram ID of the parent
    child_name: Mapped[str] = mapped_column(String(150))
    age: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(50))
    
    status: Mapped[str] = mapped_column(String(20), default="new")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
