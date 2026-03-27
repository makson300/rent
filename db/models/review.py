from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from db.models.user import User

class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    target_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    rating: Mapped[float] = mapped_column(Float)
    comment: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    target_user: Mapped["User"] = relationship("User", foreign_keys=[target_user_id], back_populates="reviews_received")
    author: Mapped["User"] = relationship("User", foreign_keys=[author_id])
