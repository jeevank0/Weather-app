import asyncio
import os

from app.services.tomorrow_service import TomorrowService


def test_tomorrow_service_uses_cache_for_same_location() -> None:
    service = TomorrowService()
    os.environ["TOMORROW_API_KEY"] = "test-key"

    call_count = {"value": 0}

    async def fake_fetch_json(_, url, __, not_found_message):
        assert isinstance(not_found_message, str)
        call_count["value"] += 1
        if url.endswith("/realtime"):
            return {
                "location": {"name": "Chennai"},
                "data": {
                    "values": {
                        "temperature": 30.0,
                        "humidity": 78,
                        "weatherCode": 4001,
                    }
                },
            }
        return {
            "timelines": {
                "daily": [
                    {
                        "time": "2026-03-17T00:00:00Z",
                        "values": {
                            "temperatureAvg": 31.0,
                            "humidityAvg": 80,
                            "weatherCodeMax": 4001,
                        },
                    }
                ],
                "hourly": [
                    {
                        "time": "2026-03-17T01:00:00Z",
                        "values": {
                            "temperature": 29.5,
                            "weatherCode": 4001,
                        },
                    }
                ],
            }
        }

    service._fetch_json = fake_fetch_json  # type: ignore[method-assign]

    async def run_test() -> None:
        first = await service.get_current_and_forecast("Chennai")
        second = await service.get_current_and_forecast("chennai")

        assert first == second
        assert call_count["value"] == 2
        assert first["map_url"].startswith(
            "https://www.google.com/maps/search/?api=1&query=")
        assert first["youtube_url"].startswith(
            "https://www.youtube.com/results?search_query=")
        assert len(first["hourly_forecast"]) == 1

    asyncio.run(run_test())
