"""
Новые модели БД для масштабирования Горизонт:
- LeasingApplication   (Фаза 36)
- PatentApplication    (Фаза 42)
- DroneTracker         (Фаза 48)
- DroneportBooking     (Фаза 47)
- AcademyCourse        (Фаза 44)
- DatasetListing       (Фаза 51)
"""
from datetime import datetime
from sqlalchemy import BigInteger, String, Boolean, DateTime, ForeignKey, Float, Integer, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base


# --- Фаза 36: Лизинг ---
class LeasingApplication(Base):
    __tablename__ = "leasing_applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    company_name: Mapped[str] = mapped_column(String(255))
    inn: Mapped[str] = mapped_column(String(20))
    contact_email: Mapped[str] = mapped_column(String(255))
    contact_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    drone_model: Mapped[str] = mapped_column(String(255))          # модель дрона
    tender_guarantee_id: Mapped[str | None] = mapped_column(String(100), nullable=True)  # ссылка на гарантирующий тендер
    requested_amount_rub: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(30), default="pending")  # pending/approved/rejected
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# --- Фаза 42: Патентное бюро ---
class PatentApplication(Base):
    __tablename__ = "patent_applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    fips_id: Mapped[str | None] = mapped_column(String(50), nullable=True, unique=True)  # ID от ФИПС
    title: Mapped[str] = mapped_column(String(512))
    ipc_codes: Mapped[str] = mapped_column(String(255))     # список через запятую: "B64U / G05D"
    abstract: Mapped[str] = mapped_column(Text)
    claims: Mapped[str] = mapped_column(Text)
    author_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    organization: Mapped[str | None] = mapped_column(String(255), nullable=True)
    inn: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_secret: Mapped[bool] = mapped_column(Boolean, default=False)  # секретное изобретение
    status: Mapped[str] = mapped_column(String(30), default="draft")  # draft/submitted/examination/published/rejected
    progress_pct: Mapped[int] = mapped_column(Integer, default=15)
    filed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# --- Фаза 48: IoT Трекеры Квазар-ID ---
class DroneTracker(Base):
    __tablename__ = "drone_trackers"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    tracker_id: Mapped[str] = mapped_column(String(30), unique=True, index=True)  # KVZR-XXXX-YYYY
    nickname: Mapped[str] = mapped_column(String(100))
    drone_model: Mapped[str] = mapped_column(String(255))
    serial_number: Mapped[str] = mapped_column(String(100))
    orvd_visible: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_altitude_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_speed_kmh: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_battery_pct: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    registered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# --- Фаза 47: Дронопорты — бронирование ---
class DroneportBooking(Base):
    __tablename__ = "droneport_bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    port_id: Mapped[str] = mapped_column(String(30), index=True)   # GRZ-DP-MSK-01
    port_name: Mapped[str] = mapped_column(String(255))
    tracker_id: Mapped[str | None] = mapped_column(String(30), nullable=True)  # linked tracker
    slot_from: Mapped[datetime] = mapped_column(DateTime)
    slot_to: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(20), default="confirmed")  # confirmed/cancelled/used
    qr_token: Mapped[str | None] = mapped_column(String(64), nullable=True)  # для разблокировки ангара
    total_rub: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# --- Фаза 44: Академия — прогресс ---
class CourseEnrollment(Base):
    __tablename__ = "course_enrollments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    course_id: Mapped[int] = mapped_column(Integer, index=True)     # внешний ID курса из каталога
    course_title: Mapped[str] = mapped_column(String(512))
    progress_pct: Mapped[int] = mapped_column(Integer, default=0)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    certificate_issued: Mapped[bool] = mapped_column(Boolean, default=False)
    cert_number: Mapped[str | None] = mapped_column(String(50), nullable=True)  # GRZ-2026-XXX
    enrolled_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# --- Фаза 51: Data Marketplace ---
class DatasetListing(Base):
    __tablename__ = "dataset_listings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    flight_id: Mapped[str] = mapped_column(String(50))          # ссылка на FlightPlan или ID полёта
    area_name: Mapped[str] = mapped_column(String(512))
    tags: Mapped[str] = mapped_column(String(255))               # "Сельхоз,RGB,Ортофото"
    size_gb: Mapped[float] = mapped_column(Float)
    resolution_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    has_lidar: Mapped[bool] = mapped_column(Boolean, default=False)
    has_thermal: Mapped[bool] = mapped_column(Boolean, default=False)
    price_usdt: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(20), default="unlisted")  # unlisted/listed/sold
    pii_sanitized: Mapped[bool] = mapped_column(Boolean, default=False)   # обезличены ли данные
    buyer_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    listed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
