from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base

class ModerationLog(Base):
    __tablename__ = "moderation_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    admin_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.telegram_id", ondelete="SET NULL"), nullable=True) # ID of admin/mod who did the action. Using telegram_id to easily link back.
    action_type: Mapped[str] = mapped_column(String(50)) # e.g., 'approve_listing', 'reject_listing', 'process_feedback', 'approve_emergency'
    entity_type: Mapped[str] = mapped_column(String(50)) # e.g., 'listing', 'feedback', 'emergency'
    entity_id: Mapped[int] = mapped_column(Integer) # ID of the listing/feedback etc.
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # Extra info (like reason for rejection)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # relationship to user for easier display in admin panel
    admin = relationship("User", foreign_keys=[admin_id], primaryjoin="ModerationLog.admin_id == User.telegram_id", viewonly=True)
