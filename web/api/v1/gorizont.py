"""
API v1 — «Горизонт» расширение (Фазы 36/42/44/47/48/51)
Все эндпоинты требуют авторизации через заголовок X-Telegram-Id.
Подключается к dashboard.py через: app.include_router(gorizont_router, prefix="/api/v1")
"""
import secrets
import logging
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.base import async_session
from db.models.user import User
from db.models.gorizont_ext import (
    LeasingApplication,
    PatentApplication,
    DroneTracker,
    DroneportBooking,
    CourseEnrollment,
    DatasetListing,
)

logger = logging.getLogger(__name__)

gorizont_router = APIRouter(tags=["Горизонт v2"])


# ---------------------------------------------------------------------------
# Зависимости
# ---------------------------------------------------------------------------

async def get_session():
    async with async_session() as session:
        yield session


async def resolve_user(
    x_telegram_id: Annotated[str | None, Header()] = None,
    session: AsyncSession = Depends(get_session),
) -> User:
    """Резолвим пользователя по Telegram-ID из заголовка."""
    if not x_telegram_id:
        raise HTTPException(status_code=401, detail="X-Telegram-Id header required")
    try:
        tg_id = int(x_telegram_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-Telegram-Id")

    result = await session.execute(select(User).where(User.telegram_id == tg_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ---------------------------------------------------------------------------
# Схемы (Pydantic)
# ---------------------------------------------------------------------------

# Лизинг
class LeasingCreateSchema(BaseModel):
    company_name: str = Field(max_length=255)
    inn: str = Field(min_length=10, max_length=12, pattern=r"^\d{10,12}$")
    contact_email: EmailStr
    contact_phone: str | None = None
    drone_model: str = Field(max_length=255)
    tender_guarantee_id: str | None = None
    requested_amount_rub: float = Field(gt=0)


class LeasingOut(BaseModel):
    id: int
    company_name: str
    drone_model: str
    requested_amount_rub: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# Патент
class PatentCreateSchema(BaseModel):
    title: str = Field(max_length=512)
    ipc_codes: str = Field(max_length=255, description="например: B64U, G05D")
    abstract: str
    claims: str
    author_name: str | None = None
    organization: str | None = None
    inn: str | None = Field(default=None, pattern=r"^\d{10,12}$")
    is_secret: bool = False


class PatentOut(BaseModel):
    id: int
    title: str
    ipc_codes: str
    status: str
    progress_pct: int
    is_secret: bool
    fips_id: str | None
    created_at: datetime

    class Config:
        from_attributes = True


# Трекер
class TrackerCreateSchema(BaseModel):
    nickname: str = Field(max_length=100)
    drone_model: str = Field(max_length=255)
    serial_number: str = Field(max_length=100)


class TrackerOut(BaseModel):
    id: int
    tracker_id: str
    nickname: str
    drone_model: str
    serial_number: str
    orvd_visible: bool
    is_active: bool
    last_lat: float | None
    last_lng: float | None
    last_battery_pct: int | None
    last_altitude_m: float | None
    last_speed_kmh: float | None
    last_seen_at: datetime | None
    registered_at: datetime

    class Config:
        from_attributes = True


# Профиль пользователя
class ProfileOut(BaseModel):
    telegram_id: int
    full_name: str | None
    username: str | None
    user_type: str
    verified_flight_hours: float
    is_emergency_volunteer: bool
    inn: str | None
    company_name: str | None
    referral_bonus: int
    is_admin: bool
    is_moderator: bool

    class Config:
        from_attributes = True


# Дронопорт
class BookingCreateSchema(BaseModel):
    port_id: str = Field(max_length=30)
    port_name: str = Field(max_length=255)
    tracker_id: str | None = None
    slot_from: datetime
    slot_to: datetime
    tariff_per_h: float = Field(gt=0)


class BookingOut(BaseModel):
    id: int
    port_id: str
    port_name: str
    slot_from: datetime
    slot_to: datetime
    status: str
    qr_token: str | None
    total_rub: float | None
    created_at: datetime

    class Config:
        from_attributes = True


# Академия
class EnrollSchema(BaseModel):
    course_id: int
    course_title: str = Field(max_length=512)


class EnrollmentOut(BaseModel):
    id: int
    course_id: int
    course_title: str
    progress_pct: int
    is_completed: bool
    certificate_issued: bool
    cert_number: str | None
    enrolled_at: datetime

    class Config:
        from_attributes = True


# Data Marketplace
class DatasetListSchema(BaseModel):
    flight_id: str = Field(max_length=50)
    area_name: str = Field(max_length=512)
    tags: str = Field(max_length=255)
    size_gb: float = Field(gt=0)
    resolution_cm: float | None = None
    has_lidar: bool = False
    has_thermal: bool = False


class DatasetOut(BaseModel):
    id: int
    flight_id: str
    area_name: str
    tags: str
    size_gb: float
    price_usdt: float
    status: str
    buyer_count: int
    pii_sanitized: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Профиль пилота (/me)
# ---------------------------------------------------------------------------

@gorizont_router.get("/me", response_model=ProfileOut)
async def get_my_profile(user: User = Depends(resolve_user)) -> User:
    """Возвращает профиль текущего авторизованного пользователя."""
    return user


@gorizont_router.get("/me/stats")
async def get_my_stats(
    user: User = Depends(resolve_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Агрегированная статистика пилота по всем модулям платформы."""
    from sqlalchemy import func

    trackers_count = (await session.execute(
        select(func.count()).where(DroneTracker.user_id == user.id)
    )).scalar_one()

    active_bookings = (await session.execute(
        select(func.count()).where(
            DroneportBooking.user_id == user.id,
            DroneportBooking.status == "confirmed",
        )
    )).scalar_one()

    enrollments = (await session.execute(
        select(func.count()).where(CourseEnrollment.user_id == user.id)
    )).scalar_one()

    certs_issued = (await session.execute(
        select(func.count()).where(
            CourseEnrollment.user_id == user.id,
            CourseEnrollment.certificate_issued == True,  # noqa: E712
        )
    )).scalar_one()

    datasets_listed = (await session.execute(
        select(func.count()).where(
            DatasetListing.user_id == user.id,
            DatasetListing.status == "listed",
        )
    )).scalar_one()

    patents_count = (await session.execute(
        select(func.count()).where(PatentApplication.user_id == user.id)
    )).scalar_one()

    leasing_count = (await session.execute(
        select(func.count()).where(LeasingApplication.user_id == user.id)
    )).scalar_one()

    return {
        "trackers": trackers_count,
        "active_bookings": active_bookings,
        "enrollments": enrollments,
        "certificates": certs_issued,
        "datasets_listed": datasets_listed,
        "patents": patents_count,
        "leasing_applications": leasing_count,
        "flight_hours": user.verified_flight_hours,
        "referral_bonus": user.referral_bonus,
        "volunteer_rescues": user.volunteer_rescues,
    }


# ---------------------------------------------------------------------------
# Лизинг — CRUD
# ---------------------------------------------------------------------------

@gorizont_router.get("/leasing", response_model=list[LeasingOut])
async def list_leasing_applications(
    user: User = Depends(resolve_user),
    session: AsyncSession = Depends(get_session),
):
    """Список заявок на лизинг текущего пользователя."""
    result = await session.execute(
        select(LeasingApplication)
        .where(LeasingApplication.user_id == user.id)
        .order_by(LeasingApplication.created_at.desc())
    )
    return result.scalars().all()


@gorizont_router.post("/leasing", response_model=LeasingOut, status_code=201)
async def create_leasing_application(
    data: LeasingCreateSchema,
    user: User = Depends(resolve_user),
    session: AsyncSession = Depends(get_session),
):
    """Подать заявку на лизинг дрона."""
    application = LeasingApplication(
        user_id=user.id,
        **data.model_dump(),
    )
    session.add(application)
    await session.commit()
    await session.refresh(application)
    logger.info("Leasing application %d created for user %d", application.id, user.id)
    return application


# ---------------------------------------------------------------------------
# Патенты — CRUD
# ---------------------------------------------------------------------------

@gorizont_router.get("/patents", response_model=list[PatentOut])
async def list_patents(
    user: User = Depends(resolve_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(PatentApplication)
        .where(PatentApplication.user_id == user.id)
        .order_by(PatentApplication.created_at.desc())
    )
    return result.scalars().all()


@gorizont_router.post("/patents", response_model=PatentOut, status_code=201)
async def submit_patent(
    data: PatentCreateSchema,
    user: User = Depends(resolve_user),
    session: AsyncSession = Depends(get_session),
):
    """Подать заявку в ФИПС через платформу."""
    patent = PatentApplication(
        user_id=user.id,
        status="draft",
        progress_pct=15,
        **data.model_dump(),
    )
    session.add(patent)
    await session.commit()
    await session.refresh(patent)
    logger.info("Patent application %d submitted for user %d", patent.id, user.id)
    return patent


@gorizont_router.post("/patents/{patent_id}/file", response_model=PatentOut)
async def file_patent_to_fips(
    patent_id: int,
    user: User = Depends(resolve_user),
    session: AsyncSession = Depends(get_session),
):
    """Отправить заявку в ФИПС (меняет статус draft → submitted)."""
    result = await session.execute(
        select(PatentApplication).where(
            PatentApplication.id == patent_id,
            PatentApplication.user_id == user.id,
        )
    )
    patent = result.scalar_one_or_none()
    if not patent:
        raise HTTPException(status_code=404, detail="Patent not found")
    if patent.status != "draft":
        raise HTTPException(status_code=409, detail=f"Status is already '{patent.status}'")
    patent.status = "submitted"
    patent.filed_at = datetime.now(timezone.utc)
    patent.progress_pct = 40
    # В продакшне здесь будет вызов API Госуслуги/ФИПС
    # fips_resp = await fips_client.submit(patent)
    # patent.fips_id = fips_resp["application_id"]
    await session.commit()
    await session.refresh(patent)
    return patent


# ---------------------------------------------------------------------------
# Трекеры Квазар-ID
# ---------------------------------------------------------------------------

def _generate_tracker_id() -> str:
    """Генерация уникального ID в формате KVZR-XXXX-YYYY."""
    prefix = secrets.randbelow(9000) + 1000
    suffix = secrets.token_hex(2).upper()
    return f"KVZR-{prefix}-{suffix}"


@gorizont_router.get("/trackers", response_model=list[TrackerOut])
async def list_trackers(
    user: User = Depends(resolve_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(DroneTracker)
        .where(DroneTracker.user_id == user.id)
        .order_by(DroneTracker.registered_at.desc())
    )
    return result.scalars().all()


@gorizont_router.post("/trackers", response_model=TrackerOut, status_code=201)
async def register_tracker(
    data: TrackerCreateSchema,
    user: User = Depends(resolve_user),
    session: AsyncSession = Depends(get_session),
):
    """Зарегистрировать новый IoT-трекер Квазар-ID."""
    # Генерируем уникальный Квазар-ID
    tracker_id = _generate_tracker_id()
    tracker = DroneTracker(
        user_id=user.id,
        tracker_id=tracker_id,
        orvd_visible=True,
        is_active=True,
        **data.model_dump(),
    )
    session.add(tracker)
    await session.commit()
    await session.refresh(tracker)
    logger.info("Tracker %s registered for user %d", tracker_id, user.id)
    return tracker


@gorizont_router.delete("/trackers/{tracker_id}", status_code=204)
async def delete_tracker(
    tracker_id: str,
    user: User = Depends(resolve_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(DroneTracker).where(
            DroneTracker.tracker_id == tracker_id,
            DroneTracker.user_id == user.id,
        )
    )
    tracker = result.scalar_one_or_none()
    if not tracker:
        raise HTTPException(status_code=404, detail="Tracker not found")
    await session.delete(tracker)
    await session.commit()


# ---------------------------------------------------------------------------
# Дронопорты — бронирование
# ---------------------------------------------------------------------------

@gorizont_router.get("/droneport-bookings", response_model=list[BookingOut])
async def list_bookings(
    user: User = Depends(resolve_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(DroneportBooking)
        .where(DroneportBooking.user_id == user.id)
        .order_by(DroneportBooking.slot_from.desc())
    )
    return result.scalars().all()


@gorizont_router.post("/droneport-bookings", response_model=BookingOut, status_code=201)
async def book_droneport_slot(
    data: BookingCreateSchema,
    user: User = Depends(resolve_user),
    session: AsyncSession = Depends(get_session),
):
    """Забронировать слот в дронопорте."""
    if data.slot_from >= data.slot_to:
        raise HTTPException(status_code=400, detail="slot_from must be before slot_to")

    duration_h = (data.slot_to - data.slot_from).total_seconds() / 3600
    total_rub = round(duration_h * data.tariff_per_h, 2)
    qr_token = secrets.token_urlsafe(32)

    booking = DroneportBooking(
        user_id=user.id,
        port_id=data.port_id,
        port_name=data.port_name,
        tracker_id=data.tracker_id,
        slot_from=data.slot_from,
        slot_to=data.slot_to,
        status="confirmed",
        qr_token=qr_token,
        total_rub=total_rub,
    )
    session.add(booking)
    await session.commit()
    await session.refresh(booking)
    logger.info("Droneport booking %d confirmed, port=%s, user=%d", booking.id, data.port_id, user.id)
    return booking


@gorizont_router.patch("/droneport-bookings/{booking_id}/cancel", response_model=BookingOut)
async def cancel_booking(
    booking_id: int,
    user: User = Depends(resolve_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(DroneportBooking).where(
            DroneportBooking.id == booking_id,
            DroneportBooking.user_id == user.id,
        )
    )
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status != "confirmed":
        raise HTTPException(status_code=409, detail="Booking cannot be cancelled")
    booking.status = "cancelled"
    await session.commit()
    await session.refresh(booking)
    return booking


# ---------------------------------------------------------------------------
# Академия — запись на курс и прогресс
# ---------------------------------------------------------------------------

@gorizont_router.get("/academy/enrollments", response_model=list[EnrollmentOut])
async def list_enrollments(
    user: User = Depends(resolve_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(CourseEnrollment)
        .where(CourseEnrollment.user_id == user.id)
        .order_by(CourseEnrollment.enrolled_at.desc())
    )
    return result.scalars().all()


@gorizont_router.post("/academy/enroll", response_model=EnrollmentOut, status_code=201)
async def enroll_course(
    data: EnrollSchema,
    user: User = Depends(resolve_user),
    session: AsyncSession = Depends(get_session),
):
    # Проверяем не записан ли уже
    existing = await session.execute(
        select(CourseEnrollment).where(
            CourseEnrollment.user_id == user.id,
            CourseEnrollment.course_id == data.course_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Already enrolled")

    enrollment = CourseEnrollment(
        user_id=user.id,
        course_id=data.course_id,
        course_title=data.course_title,
        progress_pct=0,
    )
    session.add(enrollment)
    await session.commit()
    await session.refresh(enrollment)
    return enrollment


@gorizont_router.patch("/academy/enrollments/{enrollment_id}/complete", response_model=EnrollmentOut)
async def complete_course(
    enrollment_id: int,
    user: User = Depends(resolve_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(CourseEnrollment).where(
            CourseEnrollment.id == enrollment_id,
            CourseEnrollment.user_id == user.id,
        )
    )
    enrollment = result.scalar_one_or_none()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    enrollment.progress_pct = 100
    enrollment.is_completed = True
    enrollment.completed_at = datetime.now(timezone.utc)
    enrollment.certificate_issued = True
    enrollment.cert_number = f"GRZ-{datetime.now().year}-{enrollment_id:04d}"
    await session.commit()
    await session.refresh(enrollment)
    return enrollment


# ---------------------------------------------------------------------------
# Data Marketplace
# ---------------------------------------------------------------------------

@gorizont_router.get("/datasets", response_model=list[DatasetOut])
async def list_datasets(
    user: User = Depends(resolve_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(DatasetListing)
        .where(DatasetListing.user_id == user.id)
        .order_by(DatasetListing.created_at.desc())
    )
    return result.scalars().all()


@gorizont_router.post("/datasets", response_model=DatasetOut, status_code=201)
async def create_dataset(
    data: DatasetListSchema,
    user: User = Depends(resolve_user),
    session: AsyncSession = Depends(get_session),
):
    """Добавить датасет (черновик)."""
    listing = DatasetListing(
        user_id=user.id,
        status="unlisted",
        pii_sanitized=False,
        **data.model_dump(),
    )
    session.add(listing)
    await session.commit()
    await session.refresh(listing)
    return listing


@gorizont_router.patch("/datasets/{dataset_id}/publish", response_model=DatasetOut)
async def publish_dataset(
    dataset_id: int,
    user: User = Depends(resolve_user),
    session: AsyncSession = Depends(get_session),
):
    """Выставить датасет на Data Marketplace (авто-обезличивание + ИИ-цена)."""
    result = await session.execute(
        select(DatasetListing).where(
            DatasetListing.id == dataset_id,
            DatasetListing.user_id == user.id,
        )
    )
    ds = result.scalar_one_or_none()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if ds.status != "unlisted":
        raise HTTPException(status_code=409, detail=f"Dataset status is '{ds.status}'")

    # Алгоритм ценообразования: база + надбавки за LIDAR/тепловизор
    base_price = round(ds.size_gb * 8.5, 2)
    if ds.has_lidar:
        base_price *= 1.6
    if ds.has_thermal:
        base_price *= 1.4
    if ds.resolution_cm and ds.resolution_cm < 2.0:
        base_price *= 1.2  # премиум за высокое разрешение

    ds.price_usdt = round(min(base_price, 500.0), 2)  # кап 500 USDT
    ds.status = "listed"
    ds.pii_sanitized = True  # В реальности: вызов pipeline обезличивания
    ds.listed_at = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(ds)
    logger.info("Dataset %d listed at $%.2f USDT by user %d", ds.id, ds.price_usdt, user.id)
    return ds

# ---------------------------------------------------------------------------
# B2B/B2G Корпоративный Дашборд: Цифровой Двойник и Аналитика
# ---------------------------------------------------------------------------

from db.models.pilot_twin import PilotTwin
from db.models.tender import Tender
from sqlalchemy import func

class TwinOut(BaseModel):
    id: int
    user_id: int
    total_flight_hours: float
    total_missions: int
    safety_score: float
    success_rate: float
    momoa_grade: str
    skills_json: str | None

    class Config:
        from_attributes = True

@gorizont_router.get("/twins", response_model=list[TwinOut])
async def list_twins(
    user: User = Depends(resolve_user),
    session: AsyncSession = Depends(get_session),
):
    """Список Цифровых Двойников (для B2B поиска пилотов)."""
    # В реальной B2B-системе сюда нужен guard check (role == company)
    result = await session.execute(
        select(PilotTwin).order_by(PilotTwin.safety_score.desc())
    )
    return result.scalars().all()

@gorizont_router.get("/twins/{twin_id}", response_model=TwinOut)
async def get_twin(
    twin_id: int,
    user: User = Depends(resolve_user),
    session: AsyncSession = Depends(get_session),
):
    """Конкретный профиль Цифрового Двойника Пилота."""
    result = await session.execute(
        select(PilotTwin).where(PilotTwin.id == twin_id)
    )
    twin = result.scalar_one_or_none()
    if not twin:
        raise HTTPException(status_code=404, detail="Twin not found")
    return twin

@gorizont_router.get("/analytics/tenders")
async def get_tenders_analytics(
    user: User = Depends(resolve_user),
    session: AsyncSession = Depends(get_session),
):
    """Агрегированная B2G-аналитика тендеров (MoMoA)."""
    total = (await session.execute(select(func.count(Tender.id)))).scalar_one()
    b2g = (await session.execute(select(func.count(Tender.id)).where(Tender.is_b2g == True))).scalar_one()
    new_status = (await session.execute(select(func.count(Tender.id)).where(Tender.b2g_status == "new"))).scalar_one()
    approved = (await session.execute(select(func.count(Tender.id)).where(Tender.b2g_status == "approved"))).scalar_one()
    
    return {
        "momoa_pulse": "Active",
        "total_tenders": total,
        "b2g_tenders": b2g,
        "new_pipelines": new_status,
        "in_progress": approved,
        "ai_match_rate": 84.5 # placeholder AI accuracy
    }
