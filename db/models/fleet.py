from datetime import datetime
from sqlalchemy import Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base

class FleetDrone(Base):
    __tablename__ = "fleet_drones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    name: Mapped[str] = mapped_column(String(255))
    serial_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    total_flight_hours: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Регламентные проверки
    propellers_changed_at_hours: Mapped[float] = mapped_column(Float, default=0.0)
    motors_serviced_at_hours: Mapped[float] = mapped_column(Float, default=0.0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", backref="fleet_drones")

class FleetBattery(Base):
    __tablename__ = "fleet_batteries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    name: Mapped[str] = mapped_column(String(255)) # например, АКБ #1 (Mavic 3)
    serial_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    charge_cycles: Mapped[int] = mapped_column(Integer, default=0)
    is_retired: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="fleet_batteries")
