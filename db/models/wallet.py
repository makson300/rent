from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, DateTime, Float
from sqlalchemy.sql import func
from db.base import Base

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.telegram_id"), unique=True, index=True, nullable=False)
    balance = Column(Float, default=0.0)
    hold_balance = Column(Float, default=0.0)
    currency = Column(String, default="RUB") # Or XTR
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False) # deposit, withdraw, hold, release
    status = Column(String, default="completed") # pending, completed, failed
    description = Column(String, nullable=True)
    reference_id = Column(String, nullable=True) # E.g. contract ID or listing ID
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
