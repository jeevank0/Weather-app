from datetime import UTC, date, datetime

from sqlalchemy import Date, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class WeatherRequest(Base):
    __tablename__ = "weather_requests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    location: Mapped[str] = mapped_column(String(120), index=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )
