from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith(
        "sqlite") else {},
)


def init_db() -> None:
    from app.db.models.weather_request import WeatherRequest  # noqa: F401

    Base.metadata.create_all(bind=engine)
