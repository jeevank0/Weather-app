from fastapi.testclient import TestClient

from app.main import app
from app.api.v1.endpoints import weather as weather_routes


def test_weather_crud_flow() -> None:
    with TestClient(app) as client:
        create_payload = {
            "location": "Chennai",
            "start_date": "2026-03-17",
            "end_date": "2026-03-20",
            "temperature": 32.5,
        }
        create_response = client.post("/api/v1/weather", json=create_payload)

        assert create_response.status_code == 201
        assert create_response.json()["success"] is True
        created = create_response.json()["data"]
        assert created["id"] > 0
        assert created["location"] == "Chennai"
        assert created["temperature"] == 32.5

        request_id = created["id"]

        list_response = client.get("/api/v1/weather")
        assert list_response.status_code == 200
        assert list_response.json()["success"] is True
        items = list_response.json()["data"]
        assert isinstance(items, list)
        assert len(items) >= 1

        get_response = client.get(f"/api/v1/weather/{request_id}")
        assert get_response.status_code == 200
        assert get_response.json()["success"] is True
        assert get_response.json()["data"]["id"] == request_id

        update_payload = {
            "location": "Chennai Central",
            "temperature": 31.2,
        }
        update_response = client.put(
            f"/api/v1/weather/{request_id}", json=update_payload)
        assert update_response.status_code == 200
        assert update_response.json()["success"] is True
        updated = update_response.json()["data"]
        assert updated["location"] == "Chennai Central"
        assert updated["temperature"] == 31.2

        delete_response = client.delete(f"/api/v1/weather/{request_id}")
        assert delete_response.status_code == 200
        assert delete_response.json()["success"] is True
        assert delete_response.json(
        )["data"]["message"] == "Weather request deleted successfully"

        not_found_response = client.get(f"/api/v1/weather/{request_id}")
        assert not_found_response.status_code == 404
        assert not_found_response.json()["success"] is False


def test_create_weather_rejects_invalid_date_range() -> None:
    with TestClient(app) as client:
        invalid_payload = {
            "location": "Bengaluru",
            "start_date": "2026-03-21",
            "end_date": "2026-03-20",
            "temperature": 29.0,
        }

        response = client.post("/api/v1/weather", json=invalid_payload)
        assert response.status_code == 422
        assert response.json()["success"] is False
        assert isinstance(response.json()["message"], str)


def test_weather_extras_returns_map_and_video_urls(monkeypatch) -> None:
    async def fake_get_location_extras(location: str) -> dict[str, str]:
        assert location == "Chennai"
        return {
            "map_url": "https://www.google.com/maps/search/?api=1&query=13.0827,80.2707",
            "youtube_url": "https://www.youtube.com/results?search_query=Chennai+weather",
        }

    monkeypatch.setattr(weather_routes.extras_service,
                        "get_location_extras", fake_get_location_extras)

    with TestClient(app) as client:
        response = client.get("/api/v1/weather/extras",
                              params={"location": "Chennai"})

    assert response.status_code == 200
    assert response.json()["success"] is True
    payload = response.json()["data"]
    assert payload["map_url"].startswith("https://www.google.com/maps")
    assert payload["youtube_url"].startswith("https://www.youtube.com/")


def test_weather_extras_rejects_invalid_location() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/weather/extras",
                              params={"location": "A"})

    assert response.status_code == 422
    assert response.json()["success"] is False
    assert isinstance(response.json()["message"], str)


def test_reverse_geocode_returns_city(monkeypatch) -> None:
    async def fake_reverse_geocode_city(lat: float, lon: float) -> str:
        assert round(lat, 4) == 13.0827
        assert round(lon, 4) == 80.2707
        return "Chennai"

    monkeypatch.setattr(weather_routes.tomorrow_service,
                        "reverse_geocode_city", fake_reverse_geocode_city)

    with TestClient(app) as client:
        response = client.get("/api/v1/weather/reverse-geocode",
                              params={"lat": 13.0827, "lon": 80.2707})

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["city"] == "Chennai"


def test_weather_live_supports_location_query(monkeypatch) -> None:
    async def fake_get_current_and_forecast(location: str) -> dict:
        assert location == "Chennai"
        return {
            "location": "Chennai",
            "temperature": 30.0,
            "humidity": 70,
            "weather_condition": "Clear",
            "map_url": "https://www.google.com/maps/search/?api=1&query=Chennai",
            "youtube_url": "https://www.youtube.com/results?search_query=Chennai+weather",
            "forecast_list": [],
            "hourly_forecast": [],
            "insights": [],
        }

    monkeypatch.setattr(
        weather_routes.tomorrow_service,
        "get_current_and_forecast",
        fake_get_current_and_forecast,
    )

    with TestClient(app) as client:
        response = client.get("/api/v1/weather/live",
                              params={"location": "Chennai"})

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["location"] == "Chennai"


def test_weather_live_supports_coordinates_query(monkeypatch) -> None:
    async def fake_get_current_and_forecast(location: str) -> dict:
        assert location == "13.0827,80.2707"
        return {
            "location": "Chennai",
            "temperature": 30.0,
            "humidity": 70,
            "weather_condition": "Clear",
            "map_url": "https://www.google.com/maps/search/?api=1&query=Chennai",
            "youtube_url": "https://www.youtube.com/results?search_query=Chennai+weather",
            "forecast_list": [],
            "hourly_forecast": [],
            "insights": [],
        }

    monkeypatch.setattr(
        weather_routes.tomorrow_service,
        "get_current_and_forecast",
        fake_get_current_and_forecast,
    )

    with TestClient(app) as client:
        response = client.get(
            "/api/v1/weather/live",
            params={"lat": 13.0827, "lon": 80.2707},
        )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["location"] == "Chennai"


def test_weather_export_csv_returns_file_response() -> None:
    with TestClient(app) as client:
        create_payload = {
            "location": "Mumbai",
            "start_date": "2026-03-17",
            "end_date": "2026-03-18",
            "temperature": 30.0,
        }
        create_response = client.post("/api/v1/weather", json=create_payload)
        assert create_response.status_code == 201

        response = client.get("/api/v1/weather/export",
                              params={"format": "csv"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment; filename=\"weather_export.csv\"" in response.headers[
        "content-disposition"]
    assert "id,location,start_date,end_date,temperature,created_at" in response.text


def test_weather_export_json_returns_file_response() -> None:
    with TestClient(app) as client:
        create_payload = {
            "location": "Delhi",
            "start_date": "2026-03-19",
            "end_date": "2026-03-20",
            "temperature": 28.5,
        }
        create_response = client.post("/api/v1/weather", json=create_payload)
        assert create_response.status_code == 201

        response = client.get("/api/v1/weather/export",
                              params={"format": "json"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert "attachment; filename=\"weather_export.json\"" in response.headers[
        "content-disposition"]
    payload = response.json()
    assert isinstance(payload, list)
    assert any(item["location"] == "Delhi" for item in payload)
