from app.services.weather_insight_service import WeatherInsightService


def test_generate_insights_for_humid_rainy_weather() -> None:
    service = WeatherInsightService()

    insights = service.generate_insights(
        temperature=31.0,
        humidity=82,
        weather_condition="Partly cloudy",
        forecast_list=[
            {"weather_condition": "light rain"},
            {"weather_condition": "overcast"},
        ],
    )

    messages = {item["message"] for item in insights}
    insight_types = {item["type"] for item in insights}

    assert "Rain likely, carry an umbrella before you leave." in messages
    assert "warning" in insight_types
    assert 1 <= len(insights) <= 2
    unique_pairs = {(item["message"], item["type"]) for item in insights}
    assert len(insights) == len(unique_pairs)


def test_generate_insights_returns_fallback_message() -> None:
    service = WeatherInsightService()

    insights = service.generate_insights(
        temperature=24.0,
        humidity=45,
        weather_condition="mist",
        forecast_list=[{"weather_condition": "overcast"}],
    )

    assert insights == [
        {
            "message": "Conditions look stable. Standard outdoor plans should be fine.",
            "type": "info",
        }
    ]


def test_generate_insights_for_clear_weather_outdoor_plan() -> None:
    service = WeatherInsightService()

    insights = service.generate_insights(
        temperature=27.0,
        humidity=40,
        weather_condition="clear sky",
        forecast_list=[{"weather_condition": "clear sky"}],
    )

    assert insights == [
        {
            "message": "Conditions look stable. Standard outdoor plans should be fine.",
            "type": "info",
        }
    ]


def test_generate_insights_max_two_and_no_duplicates() -> None:
    service = WeatherInsightService()

    insights = service.generate_insights(
        temperature=37.0,
        humidity=85,
        weather_condition="thunderstorm",
        forecast_list=[
            {"weather_condition": "heavy rain"},
            {"weather_condition": "windy"},
            {"weather_condition": "snow"},
        ],
    )

    assert 1 <= len(insights) <= 2
    unique_pairs = {(item["message"], item["type"]) for item in insights}
    assert len(insights) == len(unique_pairs)
    assert any(item["message"] ==
               "Rain likely, carry an umbrella before you leave." for item in insights)
    assert any(item["message"] ==
               "Snow advisory: use warm gear and be careful on roads and walkways." for item in insights)


def test_generate_insights_classifies_snow_as_warning() -> None:
    service = WeatherInsightService()

    insights = service.generate_insights(
        temperature=2.0,
        humidity=70,
        weather_condition="light snow",
        forecast_list=[{"weather_condition": "snow showers"}],
    )

    assert any(item["type"] == "warning" for item in insights)
