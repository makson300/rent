from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base


class Category(Base):
    """Категории: аренда / курсы / ЧП-события (древовидная структура)"""
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    # rent / course / chp — определяет к какому разделу относится
    type: Mapped[str] = mapped_column(String(20))
    # parent_id для подкатегорий (null = корневая)
    parent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=True
    )
