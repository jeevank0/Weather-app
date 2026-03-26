from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class WeatherRequestCreate(BaseModel):
    location: str = Field(..., min_length=2, max_length=120)
    start_date: date
    end_date: date
    temperature: float

    @field_validator("location")
    @classmethod
    def validate_location(cls, location: str) -> str:
        value = location.strip()
        if len(value) < 2:
            raise ValueError(
                "Please provide a valid location with at least 2 characters")
        return value

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, end_date: date, info):
        start_date = info.data.get("start_date")
        if start_date and end_date < start_date:
            raise ValueError("End date cannot be earlier than start date")
        return end_date


class WeatherRequestUpdate(BaseModel):
    location: str | None = Field(default=None, min_length=2, max_length=120)
    start_date: date | None = None
    end_date: date | None = None
    temperature: float | None = None

    @field_validator("location")
    @classmethod
    def validate_optional_location(cls, location: str | None) -> str | None:
        if location is None:
            return None
        value = location.strip()
        if len(value) < 2:
            raise ValueError(
                "Please provide a valid location with at least 2 characters")
        return value

    @model_validator(mode="after")
    def validate_payload_and_date_range(self):
        if (
            self.location is None
            and self.start_date is None
            and self.end_date is None
            and self.temperature is None
        ):
            raise ValueError("At least one field is required for update")

        if self.start_date is not None and self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("End date cannot be earlier than start date")

        return self


class WeatherRequestRead(BaseModel):
    id: int
    location: str
    start_date: date
    end_date: date
    temperature: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WeatherRequestItemResponse(BaseModel):
    success: bool = True
    data: WeatherRequestRead


class WeatherRequestListResponse(BaseModel):
    success: bool = True
    data: list[WeatherRequestRead]


class MessageData(BaseModel):
    message: str


class MessageResponse(BaseModel):
    success: bool = True
    data: MessageData


class ForecastDay(BaseModel):
    date: date
    temperature: float
    humidity: int
    weather_condition: str


class HourlyForecastPoint(BaseModel):
    time: datetime
    temperature: float
    weather_condition: str


class WeatherInsight(BaseModel):
    message: str
    type: Literal["info", "warning", "alert"]


class LiveWeatherData(BaseModel):
    location: str
    temperature: float
    humidity: int
    weather_condition: str
    map_url: str
    youtube_url: str
    forecast_list: list[ForecastDay]
    hourly_forecast: list[HourlyForecastPoint]
    insights: list[WeatherInsight]


class LiveWeatherResponse(BaseModel):
    success: bool = True
    data: LiveWeatherData


class WeatherExtrasData(BaseModel):
    map_url: str
    youtube_url: str


class WeatherExtrasResponse(BaseModel):
    success: bool = True
    data: WeatherExtrasData


class ReverseGeocodeData(BaseModel):
    city: str


class ReverseGeocodeResponse(BaseModel):
    success: bool = True
    data: ReverseGeocodeData
