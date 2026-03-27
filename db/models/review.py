from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from db.models.user import User
    from db.models.listing import Listing

class Review(Base):
    """Модель для отзывов и рейтингов (для пользователей и/или объявлений)"""
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    target_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    listing_id: Mapped[int | None] = mapped_column(ForeignKey("listings.id"), nullable=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    rating: Mapped[float] = mapped_column(Float, default=5.0)
    comment: Mapped[str | None] = mapped_column(String(500), nullable=True)
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    target_user: Mapped["User"] = relationship("User", foreign_keys=[target_user_id], back_populates="reviews_received", overlaps="user")
    author: Mapped["User"] = relationship("User", foreign_keys=[author_id], overlaps="user")
    listing: Mapped["Listing"] = relationship("Listing", back_populates="reviews")
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], overlaps="author,target_user")
