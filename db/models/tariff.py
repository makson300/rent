from sqlalchemy import String, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base


class Tariff(Base):
    """Тарифы для размещения объявлений (аренда / курсы)"""
    __tablename__ = "tariffs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    duration_days: Mapped[int] = mapped_column(Integer)
    listings_count: Mapped[int] = mapped_column(Integer, default=1)
    # rent / course — к какому разделу относится тариф
    type: Mapped[str] = mapped_column(String(20))
