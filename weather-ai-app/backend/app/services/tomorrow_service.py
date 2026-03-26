import copy
import logging
import os
import time
from datetime import datetime
from typing import Any

import httpx

from app.core.config import settings
from app.services.extras_service import ExtrasService
from app.services.weather_insight_service import WeatherInsightService


class TomorrowLocationNotFoundError(Exception):
    pass


class TomorrowServiceError(Exception):
    pass


class TomorrowService:
    CACHE_TTL_SECONDS = 600

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.base_url = settings.tomorrow_base_url.rstrip("/")
        self.insight_service = WeatherInsightService()
        self.extras_service = ExtrasService()
        self._weather_cache: dict[str, tuple[float, dict[str, Any]]] = {}

    async def get_current_and_forecast(self, location: str) -> dict[str, Any]:
        normalized_location = location.strip()
        if len(normalized_location) < 2:
            raise ValueError(
                "Please provide a valid location with at least 2 characters")

        api_key = self._get_api_key()

        cache_key = self._cache_key(normalized_location)
        cached_weather = self._get_cached_weather(cache_key)
        if cached_weather is not None:
            self.logger.info(
                "weather_fetch_cache_hit endpoint=/weather/live status=200 location=%s",
                normalized_location,
            )
            return cached_weather

        self.logger.info(
            "weather_fetch_cache_miss endpoint=/weather/live status=200 location=%s",
            normalized_location,
        )

        current_params = {
            "location": normalized_location,
            "apikey": api_key,
            "units": "metric",
        }
        forecast_params = {
            "location": normalized_location,
            "apikey": api_key,
            "units": "metric",
            "timesteps": "1d,1h",
        }

        async with httpx.AsyncClient(timeout=12.0) as client:
            current_data = await self._fetch_json(
                client,
                f"{self.base_url}/realtime",
                current_params,
                not_found_message=f"No weather data found for '{normalized_location}'",
            )
            forecast_data = await self._fetch_json(
                client,
                f"{self.base_url}/forecast",
                forecast_params,
                not_found_message=f"Forecast not found for '{normalized_location}'",
            )

        self.logger.info(
            "weather_fetch_success endpoint=/weather/live status=200 location=%s",
            normalized_location,
        )

        values = current_data.get("data", {}).get("values", {})
        temperature = float(values.get("temperature", 0.0))
        humidity = int(values.get("humidity", 0))
        condition = self._extract_weather_condition(current_data)
        forecast_list = self._build_forecast_list(forecast_data)
        hourly_forecast = self._build_hourly_forecast(forecast_data)
        insights = self.insight_service.generate_insights(
            temperature=temperature,
            humidity=humidity,
            weather_condition=condition,
            forecast_list=forecast_list,
        )
        resolved_location = str(
            current_data.get("location", {}).get("name", normalized_location)
        )
        extras = await self.extras_service.get_location_extras(resolved_location)

        weather_data = {
            "location": resolved_location,
            "temperature": temperature,
            "humidity": humidity,
            "weather_condition": condition,
            "map_url": extras["map_url"],
            "youtube_url": extras["youtube_url"],
            "forecast_list": forecast_list,
            "hourly_forecast": hourly_forecast,
            "insights": insights,
        }
        self._set_cached_weather(cache_key, weather_data)
        return weather_data

    async def reverse_geocode_city(self, lat: float, lon: float) -> str:
        api_key = self._get_api_key()
        if lat < -90 or lat > 90:
            raise ValueError("Latitude must be between -90 and 90")
        if lon < -180 or lon > 180:
            raise ValueError("Longitude must be between -180 and 180")

        params = {
            "location": f"{lat},{lon}",
            "apikey": api_key,
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{self.base_url}/realtime", params=params)

        self.logger.info(
            "weather_reverse_geocode_call endpoint=/weather/reverse-geocode status=%s lat=%.4f lon=%.4f",
            response.status_code,
            lat,
            lon,
        )

        if response.status_code == 401:
            raise TomorrowServiceError("Invalid Tomorrow.io API key")
        if response.status_code in (400, 404, 422):
            raise TomorrowLocationNotFoundError(
                "Could not determine city from your coordinates")
        if response.status_code >= 400:
            raise TomorrowServiceError("Failed to reverse geocode location")

        payload = self._safe_json(response)
        name = str(payload.get("location", {}).get("name", "")).strip()
        if not name:
            raise TomorrowLocationNotFoundError(
                "Could not determine city from your coordinates")

        city = name.split(",")[0].strip()
        if not city:
            raise TomorrowLocationNotFoundError(
                "Could not determine city from your coordinates")
        return city

    async def _fetch_json(
        self,
        client: httpx.AsyncClient,
        url: str,
        params: dict[str, Any],
        not_found_message: str,
    ) -> dict[str, Any]:
        response = await client.get(url, params=params)

        self.logger.info(
            "tomorrow_http_call endpoint=%s status=%s",
            url,
            response.status_code,
        )

        if response.status_code == 404:
            raise TomorrowLocationNotFoundError(not_found_message)
        if response.status_code == 401:
            raise TomorrowServiceError("Invalid Tomorrow.io API key")
        if response.status_code in (400, 422):
            payload = self._safe_json(response)
            detail = str(payload.get("message", "")).lower()
            if "location" in detail:
                raise TomorrowLocationNotFoundError(not_found_message)
            raise TomorrowServiceError(
                str(payload.get("message", "Invalid weather request")))
        if response.status_code >= 400:
            message = "Failed to fetch weather data from Tomorrow.io"
            payload = self._safe_json(response)
            message = str(payload.get("message", message))
            raise TomorrowServiceError(message)

        return self._safe_json(response)

    def _build_forecast_list(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        entries = payload.get("timelines", {}).get("daily") or []
        if not isinstance(entries, list):
            return []

        forecast: list[dict[str, Any]] = []
        for item in entries:
            iso_time = item.get("time")
            if not iso_time:
                continue

            try:
                day = datetime.fromisoformat(
                    str(iso_time).replace("Z", "+00:00")).date()
            except ValueError:
                continue

            values = item.get("values") or {}
            weather_code = values.get("weatherCodeMax")
            if weather_code is None:
                weather_code = values.get("weatherCode")

            forecast.append(
                {
                    "date": day,
                    "temperature": float(
                        values.get(
                            "temperatureAvg",
                            values.get("temperatureMax", values.get(
                                "temperatureMin", 0.0)),
                        )
                    ),
                    "humidity": int(values.get("humidityAvg", values.get("humidity", 0))),
                    "weather_condition": self._weather_code_to_condition(weather_code),
                }
            )

            if len(forecast) == 5:
                break

        return forecast

    def _build_hourly_forecast(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        entries = payload.get("timelines", {}).get("hourly") or []
        if not isinstance(entries, list):
            return []

        hourly: list[dict[str, Any]] = []
        for item in entries[:24]:
            iso_time = item.get("time")
            if not iso_time:
                continue

            try:
                timestamp = datetime.fromisoformat(
                    str(iso_time).replace("Z", "+00:00"))
            except ValueError:
                continue

            values = item.get("values") or {}
            hourly.append(
                {
                    "time": timestamp,
                    "temperature": float(values.get("temperature", 0.0)),
                    "weather_condition": self._weather_code_to_condition(values.get("weatherCode")),
                }
            )

        return hourly

    @staticmethod
    def _cache_key(location: str) -> str:
        return location.strip().lower()

    @staticmethod
    def _get_api_key() -> str:
        api_key = os.getenv("TOMORROW_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("TOMORROW_API_KEY is not configured")
        return api_key

    def _get_cached_weather(self, key: str) -> dict[str, Any] | None:
        entry = self._weather_cache.get(key)
        if entry is None:
            return None

        cached_at, payload = entry
        if time.monotonic() - cached_at > self.CACHE_TTL_SECONDS:
            self._weather_cache.pop(key, None)
            return None

        return copy.deepcopy(payload)

    def _set_cached_weather(self, key: str, payload: dict[str, Any]) -> None:
        self._weather_cache[key] = (time.monotonic(), copy.deepcopy(payload))

    @staticmethod
    def _extract_weather_condition(payload: dict[str, Any]) -> str:
        code = payload.get("data", {}).get("values", {}).get("weatherCode")
        return TomorrowService._weather_code_to_condition(code)

    @staticmethod
    def _weather_code_to_condition(code: Any) -> str:
        mapping = {
            0: "Unknown",
            1000: "Clear",
            1001: "Cloudy",
            1100: "Mostly Clear",
            1101: "Partly Cloudy",
            1102: "Mostly Cloudy",
            2000: "Fog",
            2100: "Light Fog",
            3000: "Light Wind",
            3001: "Wind",
            3002: "Strong Wind",
            4000: "Drizzle",
            4001: "Rain",
            4200: "Light Rain",
            4201: "Heavy Rain",
            5000: "Snow",
            5001: "Flurries",
            5100: "Light Snow",
            5101: "Heavy Snow",
            6000: "Freezing Drizzle",
            6001: "Freezing Rain",
            6200: "Light Freezing Rain",
            6201: "Heavy Freezing Rain",
            7000: "Ice Pellets",
            7101: "Heavy Ice Pellets",
            7102: "Light Ice Pellets",
            8000: "Thunderstorm",
        }
        try:
            code_int = int(code)
        except (TypeError, ValueError):
            return "Unknown"
        return mapping.get(code_int, "Unknown")

    @staticmethod
    def _safe_json(response: httpx.Response) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError:
            return {}
        if isinstance(payload, dict):
            return payload
        return {}
