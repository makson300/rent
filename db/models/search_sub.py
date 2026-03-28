from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.base import Base

class SearchSubscription(Base):
    __tablename__ = 'search_subscriptions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), index=True, nullable=False)
    city = Column(String)  # Город, если искали по городу
    keyword = Column(String) # Ключевое слово, если искали по слову
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
