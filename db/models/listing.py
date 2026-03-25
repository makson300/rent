from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base


class Listing(Base):
    """Объявления об аренде"""
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    
    user: Mapped["User"] = relationship("User", back_populates="listings")

    
    city: Mapped[str] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    deposit_terms: Mapped[str] = mapped_column(Text)
    delivery_terms: Mapped[str] = mapped_column(Text)
    price_list: Mapped[str] = mapped_column(Text)
    contacts: Mapped[str] = mapped_column(String(150))
    
    # rental / sale
    listing_type: Mapped[str] = mapped_column(String(20), default="rental")
    # if it's from a partner
    partner_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # status: moderation / active / rejected / expired
    status: Mapped[str] = mapped_column(String(20), default="moderation")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    photos: Mapped[list["ListingPhoto"]] = relationship(
        "ListingPhoto", back_populates="listing", cascade="all, delete-orphan"
    )


class ListingPhoto(Base):
    """Фотографии для объявлений"""
    __tablename__ = "listing_photos"

    id: Mapped[int] = mapped_column(primary_key=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"))
    photo_id: Mapped[str] = mapped_column(String(200))  # Telegram file_id
    order: Mapped[int] = mapped_column(Integer, default=0)

    listing: Mapped["Listing"] = relationship("Listing", back_populates="photos")
