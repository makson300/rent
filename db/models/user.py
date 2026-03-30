from datetime import datetime
from sqlalchemy import BigInteger, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from db.models.listing import Listing
    from db.models.feedback import Feedback
    from db.models.review import Review
    from db.models.reward import Reward


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    first_name: Mapped[str] = mapped_column(String(150), default="")
    last_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    user_type: Mapped[str] = mapped_column(String(20), default="private") # private / company
    ad_slots: Mapped[int] = mapped_column(default=0)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_moderator: Mapped[bool] = mapped_column(Boolean, default=False)
    volunteer_rescues: Mapped[int] = mapped_column(default=0)
    verified_flight_hours: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Phase 28: Emergency Volunteer
    is_emergency_volunteer: Mapped[bool] = mapped_column(Boolean, default=False)
    emergency_region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # B2B DaData Verification
    inn: Mapped[str | None] = mapped_column(String(20), nullable=True)
    company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    referrer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    referral_bonus: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Связи
    listings: Mapped[list["Listing"]] = relationship("Listing", back_populates="user")
    feedbacks: Mapped[list["Feedback"]] = relationship("Feedback", back_populates="user")
    reviews_received: Mapped[list["Review"]] = relationship("Review", foreign_keys="Review.target_user_id", back_populates="target_user")
    rewards: Mapped[list["Reward"]] = relationship("Reward", back_populates="user")
