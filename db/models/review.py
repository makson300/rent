from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Text, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base


class Review(Base):
    """Отзывы и рейтинги пользователей/объявлений"""
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    listing_id: Mapped[int | None] = mapped_column(ForeignKey("listings.id"), nullable=True)
    from_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    to_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    rating: Mapped[int] = mapped_column(Integer) # 1-5
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    listing: Mapped["Listing"] = relationship("Listing", back_populates="reviews")
    author: Mapped["User"] = relationship("User", foreign_keys=[from_user_id])
    subject: Mapped["User"] = relationship("User", foreign_keys=[to_user_id], back_populates="reviews_received")
