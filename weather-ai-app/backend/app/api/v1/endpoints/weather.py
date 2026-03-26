import io
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.weather import (
    LiveWeatherResponse,
    MessageResponse,
    ReverseGeocodeResponse,
    WeatherExtrasResponse,
    WeatherRequestCreate,
    WeatherRequestItemResponse,
    WeatherRequestListResponse,
    WeatherRequestUpdate,
)
from app.services.weather_service import WeatherService
from app.services.weather_export_service import WeatherExportService
from app.services.tomorrow_service import (
    TomorrowLocationNotFoundError,
    TomorrowService,
    TomorrowServiceError,
)
from app.services.extras_service import ExtrasService

router = APIRouter(tags=["weather"])
logger = logging.getLogger(__name__)
service = WeatherService()
export_service = WeatherExportService()
tomorrow_service = TomorrowService()
extras_service = ExtrasService()


@router.get("/weather/live", response_model=LiveWeatherResponse)
async def get_live_weather(
    location: str | None = Query(default=None, min_length=2, max_length=120),
    lat: float | None = Query(default=None),
    lon: float | None = Query(default=None),
) -> LiveWeatherResponse:
    resolved_location = location.strip() if location else ""

    if not resolved_location:
        if lat is None and lon is None:
            raise HTTPException(
                status_code=422,
                detail="Provide either location or both lat and lon",
            )
        if lat is None or lon is None:
            raise HTTPException(
                status_code=422,
                detail="Both lat and lon are required when location is not provided",
            )
        resolved_location = f"{lat},{lon}"

    try:
        data = await tomorrow_service.get_current_and_forecast(location=resolved_location)
        return {"success": True, "data": data}
    except ValueError as exc:
        logger.warning(
            "weather_live_validation_error endpoint=/weather/live status=422 error=%s", exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except TomorrowLocationNotFoundError as exc:
        logger.warning(
            "weather_live_not_found endpoint=/weather/live status=404 error=%s", exc)
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except TomorrowServiceError as exc:
        logger.error(
            "weather_live_upstream_error endpoint=/weather/live status=502 error=%s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except RuntimeError as exc:
        logger.error(
            "weather_live_runtime_error endpoint=/weather/live status=500 error=%s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/weather/reverse-geocode", response_model=ReverseGeocodeResponse)
async def reverse_geocode_city(
    lat: float = Query(...),
    lon: float = Query(...),
) -> ReverseGeocodeResponse:
    try:
        city = await tomorrow_service.reverse_geocode_city(lat=lat, lon=lon)
        return {"success": True, "data": {"city": city}}
    except ValueError as exc:
        logger.warning(
            "reverse_geocode_validation_error endpoint=/weather/reverse-geocode status=422 error=%s", exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except TomorrowLocationNotFoundError as exc:
        logger.warning(
            "reverse_geocode_not_found endpoint=/weather/reverse-geocode status=404 error=%s", exc)
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except TomorrowServiceError as exc:
        logger.error(
            "reverse_geocode_upstream_error endpoint=/weather/reverse-geocode status=502 error=%s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except RuntimeError as exc:
        logger.error(
            "reverse_geocode_runtime_error endpoint=/weather/reverse-geocode status=500 error=%s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/weather/extras", response_model=WeatherExtrasResponse)
async def get_weather_extras(
    location: str = Query(..., min_length=2, max_length=120),
) -> WeatherExtrasResponse:
    try:
        data = await extras_service.get_location_extras(location=location)
        return {"success": True, "data": data}
    except ValueError as exc:
        logger.warning(
            "weather_extras_validation_error endpoint=/weather/extras status=422 error=%s", exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/weather", response_model=WeatherRequestItemResponse, status_code=201)
def create_weather_request(payload: WeatherRequestCreate, db: Session = Depends(get_db)) -> WeatherRequestItemResponse:
    try:
        weather_request = service.create_weather_request(
            payload=payload, db=db)
        return {"success": True, "data": weather_request}
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception(
            "create_weather_request_failed endpoint=/weather status=500")
        raise HTTPException(
            status_code=500, detail="Failed to create weather request") from exc


@router.get("/weather", response_model=WeatherRequestListResponse)
def list_weather_requests(db: Session = Depends(get_db)) -> WeatherRequestListResponse:
    try:
        weather_requests = service.list_weather_requests(db=db)
        return {"success": True, "data": weather_requests}
    except SQLAlchemyError as exc:
        logger.exception(
            "list_weather_requests_failed endpoint=/weather status=500")
        raise HTTPException(
            status_code=500, detail="Failed to list weather requests") from exc


@router.get("/weather/export")
def export_weather_requests(
    format: str = Query(..., pattern="^(csv|json)$"),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    try:
        weather_requests = service.list_weather_requests(db=db)
    except SQLAlchemyError as exc:
        logger.exception(
            "export_weather_requests_failed endpoint=/weather/export status=500")
        raise HTTPException(
            status_code=500, detail="Failed to load weather requests for export") from exc

    selected_format = format.lower()
    if selected_format == "csv":
        csv_content = export_service.build_csv_content(weather_requests)
        filename = "weather_export.csv"
        return StreamingResponse(
            io.BytesIO(csv_content.encode("utf-8")),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    json_content = export_service.build_json_content(weather_requests)
    filename = "weather_export.json"
    return StreamingResponse(
        io.BytesIO(json_content.encode("utf-8")),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/weather/{request_id}", response_model=WeatherRequestItemResponse)
def get_weather_request(request_id: int, db: Session = Depends(get_db)) -> WeatherRequestItemResponse:
    try:
        weather_request = service.get_weather_request_by_id(
            request_id=request_id, db=db)
        if weather_request is None:
            logger.warning(
                "get_weather_request_not_found endpoint=/weather/%s status=404", request_id)
            raise HTTPException(
                status_code=404, detail="Weather request not found")
        return {"success": True, "data": weather_request}
    except SQLAlchemyError as exc:
        logger.exception(
            "get_weather_request_failed endpoint=/weather/%s status=500", request_id)
        raise HTTPException(
            status_code=500, detail="Failed to fetch weather request") from exc


@router.put("/weather/{request_id}", response_model=WeatherRequestItemResponse)
def update_weather_request(
    request_id: int,
    payload: WeatherRequestUpdate,
    db: Session = Depends(get_db),
) -> WeatherRequestItemResponse:
    try:
        weather_request = service.update_weather_request(
            request_id=request_id, payload=payload, db=db)
        if weather_request is None:
            logger.warning(
                "update_weather_request_not_found endpoint=/weather/%s status=404", request_id)
            raise HTTPException(
                status_code=404, detail="Weather request not found")
        return {"success": True, "data": weather_request}
    except ValueError as exc:
        logger.warning(
            "update_weather_request_validation_error endpoint=/weather/%s status=422 error=%s", request_id, exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception(
            "update_weather_request_failed endpoint=/weather/%s status=500", request_id)
        raise HTTPException(
            status_code=500, detail="Failed to update weather request") from exc


@router.delete("/weather/{request_id}", response_model=MessageResponse)
def delete_weather_request(request_id: int, db: Session = Depends(get_db)) -> MessageResponse:
    try:
        deleted = service.delete_weather_request(request_id=request_id, db=db)
        if not deleted:
            logger.warning(
                "delete_weather_request_not_found endpoint=/weather/%s status=404", request_id)
            raise HTTPException(
                status_code=404, detail="Weather request not found")
        return {"success": True, "data": {"message": "Weather request deleted successfully"}}
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception(
            "delete_weather_request_failed endpoint=/weather/%s status=500", request_id)
        raise HTTPException(
            status_code=500, detail="Failed to delete weather request") from exc
