from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from db.base import Base

class FlightPlan(Base):
    __tablename__ = 'flight_plans'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # parameters
    coords = Column(String(50))
    radius = Column(String(20))
    alt_min = Column(String(20))
    alt_max = Column(String(20))
    time_start = Column(String(20))
    time_end = Column(String(20))
    task_desc = Column(String(200))
    operator_name = Column(String(100))
    phone = Column(String(20))
    
    # Generated exact text sent to ORVD
    shr_code = Column(Text, nullable=False)
    
    # State tracking: 'draft', 'pending', 'approved', 'rejected'
    status = Column(String(50), default='pending')
    is_emergency = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", backref="flight_plans")
