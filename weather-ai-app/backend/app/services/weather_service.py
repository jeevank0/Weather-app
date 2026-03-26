from sqlalchemy.orm import Session

from app.db.models.weather_request import WeatherRequest
from app.schemas.weather import WeatherRequestCreate, WeatherRequestUpdate


class WeatherService:
    def create_weather_request(self, payload: WeatherRequestCreate, db: Session) -> WeatherRequest:
        record = WeatherRequest(
            location=payload.location.strip(),
            start_date=payload.start_date,
            end_date=payload.end_date,
            temperature=payload.temperature,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def list_weather_requests(self, db: Session, location: str | None = None) -> list[WeatherRequest]:
        query = db.query(WeatherRequest)
        if location:
            query = query.filter(
                WeatherRequest.location.ilike(f"%{location.strip()}%"))
        return query.order_by(WeatherRequest.created_at.desc()).all()

    def get_weather_request_by_id(self, request_id: int, db: Session) -> WeatherRequest | None:
        return db.query(WeatherRequest).filter(WeatherRequest.id == request_id).first()

    def update_weather_request(
        self,
        request_id: int,
        payload: WeatherRequestUpdate,
        db: Session,
    ) -> WeatherRequest | None:
        record = self.get_weather_request_by_id(request_id=request_id, db=db)
        if record is None:
            return None

        merged_start_date = payload.start_date if payload.start_date is not None else record.start_date
        merged_end_date = payload.end_date if payload.end_date is not None else record.end_date
        if merged_end_date < merged_start_date:
            raise ValueError("End date cannot be earlier than start date")

        if payload.location is not None:
            record.location = payload.location.strip()
        if payload.start_date is not None:
            record.start_date = payload.start_date
        if payload.end_date is not None:
            record.end_date = payload.end_date
        if payload.temperature is not None:
            record.temperature = payload.temperature

        db.commit()
        db.refresh(record)
        return record

    def delete_weather_request(self, request_id: int, db: Session) -> bool:
        record = self.get_weather_request_by_id(request_id=request_id, db=db)
        if record is None:
            return False

        db.delete(record)
        db.commit()
        return True
