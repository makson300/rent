from datetime import datetime
from sqlalchemy import Integer, ForeignKey, Text, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base

class Review(Base):
    """Модель для отзывов и рейтингов"""
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    rating: Mapped[float] = mapped_column(Float, default=5.0)
    text: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Связи
    listing: Mapped["Listing"] = relationship("Listing", back_populates="reviews")
    user: Mapped["User"] = relationship("User")
