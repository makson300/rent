"""add_gorizont_ext_tables

Revision ID: 7447e3e6b5c0
Revises: 3458b369c9cc
Create Date: 2026-03-30 20:42:51.190521

Горизонт v2: добавляем таблицы для фаз 36/42/44/47/48/51.
Используем raw SQL с IF NOT EXISTS — безопасно при любом состоянии БД
(init_db() может создать таблицы раньше миграций).
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers
revision: str = "7447e3e6b5c0"
down_revision: Union[str, None] = "3458b369c9cc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # ------------------------------------------------------------------
    # Фаза 44: Академия — запись на курс и прогресс
    # ------------------------------------------------------------------
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS course_enrollments (
            id               INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            user_id          INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            course_id        INTEGER NOT NULL,
            course_title     VARCHAR(512) NOT NULL,
            progress_pct     INTEGER NOT NULL DEFAULT 0,
            is_completed     BOOLEAN NOT NULL DEFAULT 0,
            completed_at     DATETIME,
            certificate_issued BOOLEAN NOT NULL DEFAULT 0,
            cert_number      VARCHAR(50),
            enrolled_at      DATETIME NOT NULL
        )
    """))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_course_enrollments_user_id   ON course_enrollments(user_id)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_course_enrollments_course_id ON course_enrollments(course_id)"
    ))

    # ------------------------------------------------------------------
    # Фаза 51: Data Marketplace — датасеты для монетизации
    # ------------------------------------------------------------------
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS dataset_listings (
            id             INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            flight_id      VARCHAR(50)  NOT NULL,
            area_name      VARCHAR(512) NOT NULL,
            tags           VARCHAR(255) NOT NULL,
            size_gb        FLOAT NOT NULL,
            resolution_cm  FLOAT,
            has_lidar      BOOLEAN NOT NULL DEFAULT 0,
            has_thermal    BOOLEAN NOT NULL DEFAULT 0,
            price_usdt     FLOAT NOT NULL DEFAULT 0,
            status         VARCHAR(20) NOT NULL DEFAULT 'unlisted',
            pii_sanitized  BOOLEAN NOT NULL DEFAULT 0,
            buyer_count    INTEGER NOT NULL DEFAULT 0,
            created_at     DATETIME NOT NULL,
            listed_at      DATETIME
        )
    """))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_dataset_listings_user_id ON dataset_listings(user_id)"
    ))

    # ------------------------------------------------------------------
    # Фаза 48: IoT Квазар-ID трекеры
    # ------------------------------------------------------------------
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS drone_trackers (
            id               INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            user_id          INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            tracker_id       VARCHAR(30) NOT NULL UNIQUE,
            nickname         VARCHAR(100) NOT NULL,
            drone_model      VARCHAR(255) NOT NULL,
            serial_number    VARCHAR(100) NOT NULL,
            orvd_visible     BOOLEAN NOT NULL DEFAULT 1,
            is_active        BOOLEAN NOT NULL DEFAULT 1,
            last_lat         FLOAT,
            last_lng         FLOAT,
            last_altitude_m  FLOAT,
            last_speed_kmh   FLOAT,
            last_battery_pct INTEGER,
            last_seen_at     DATETIME,
            registered_at    DATETIME NOT NULL
        )
    """))
    conn.execute(sa.text(
        "CREATE UNIQUE INDEX IF NOT EXISTS ix_drone_trackers_tracker_id ON drone_trackers(tracker_id)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_drone_trackers_user_id ON drone_trackers(user_id)"
    ))

    # ------------------------------------------------------------------
    # Фаза 47: Дронопорты — бронирование слотов
    # ------------------------------------------------------------------
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS droneport_bookings (
            id         INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            port_id    VARCHAR(30)  NOT NULL,
            port_name  VARCHAR(255) NOT NULL,
            tracker_id VARCHAR(30),
            slot_from  DATETIME NOT NULL,
            slot_to    DATETIME NOT NULL,
            status     VARCHAR(20) NOT NULL DEFAULT 'confirmed',
            qr_token   VARCHAR(64),
            total_rub  FLOAT,
            created_at DATETIME NOT NULL
        )
    """))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_droneport_bookings_user_id ON droneport_bookings(user_id)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_droneport_bookings_port_id ON droneport_bookings(port_id)"
    ))

    # ------------------------------------------------------------------
    # Фаза 36: B2B Лизинг дронов
    # ------------------------------------------------------------------
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS leasing_applications (
            id                    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            user_id               INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            company_name          VARCHAR(255) NOT NULL,
            inn                   VARCHAR(20)  NOT NULL,
            contact_email         VARCHAR(255) NOT NULL,
            contact_phone         VARCHAR(30),
            drone_model           VARCHAR(255) NOT NULL,
            tender_guarantee_id   VARCHAR(100),
            requested_amount_rub  FLOAT NOT NULL,
            status                VARCHAR(30) NOT NULL DEFAULT 'pending',
            created_at            DATETIME NOT NULL,
            updated_at            DATETIME NOT NULL
        )
    """))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_leasing_applications_user_id ON leasing_applications(user_id)"
    ))

    # ------------------------------------------------------------------
    # Фаза 42: Патентное бюро
    # ------------------------------------------------------------------
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS patent_applications (
            id           INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            fips_id      VARCHAR(50) UNIQUE,
            title        VARCHAR(512) NOT NULL,
            ipc_codes    VARCHAR(255) NOT NULL,
            abstract     TEXT NOT NULL,
            claims       TEXT NOT NULL,
            author_name  VARCHAR(255),
            organization VARCHAR(255),
            inn          VARCHAR(20),
            is_secret    BOOLEAN NOT NULL DEFAULT 0,
            status       VARCHAR(30) NOT NULL DEFAULT 'draft',
            progress_pct INTEGER NOT NULL DEFAULT 15,
            filed_at     DATETIME,
            created_at   DATETIME NOT NULL
        )
    """))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_patent_applications_user_id ON patent_applications(user_id)"
    ))

    # ------------------------------------------------------------------
    # Новые колонки в существующих таблицах (idempotent)
    # SQLite: ALTER TABLE ADD COLUMN падает если колонка уже есть — ловим
    # ------------------------------------------------------------------
    idempotent_alters = [
        "ALTER TABLE users ADD COLUMN is_emergency_volunteer BOOLEAN DEFAULT 0",
        "ALTER TABLE users ADD COLUMN emergency_region VARCHAR(100)",
        "ALTER TABLE users ADD COLUMN inn VARCHAR(20)",
        "ALTER TABLE users ADD COLUMN company_name VARCHAR(255)",
        "ALTER TABLE tenders ADD COLUMN lat FLOAT",
        "ALTER TABLE tenders ADD COLUMN lng FLOAT",
        "ALTER TABLE tender_bids ADD COLUMN ai_reason TEXT",
    ]
    for stmt in idempotent_alters:
        try:
            conn.execute(sa.text(stmt))
        except Exception:
            pass  # колонка уже существует


def downgrade() -> None:
    conn = op.get_bind()
    for table in [
        "patent_applications",
        "leasing_applications",
        "droneport_bookings",
        "drone_trackers",
        "dataset_listings",
        "course_enrollments",
    ]:
        conn.execute(sa.text(f"DROP TABLE IF EXISTS {table}"))
