class WeatherInsightService:
    MAX_INSIGHTS = 2

    def generate_insights(
        self,
        temperature: float,
        humidity: int,
        weather_condition: str,
        forecast_list: list[dict],
    ) -> list[dict[str, str]]:
        insights: list[dict[str, str]] = []
        seen: set[tuple[str, str]] = set()

        condition_text = (weather_condition or "").lower()
        forecast_conditions = [
            str(item.get("weather_condition", "")).lower() for item in forecast_list]
        all_conditions = [condition_text, *forecast_conditions]

        is_rainy = any(self._contains_any(condition, [
                       "rain", "drizzle", "shower", "thunderstorm"]) for condition in all_conditions)
        is_snowy = any(self._contains_any(
            condition, ["snow", "sleet", "blizzard"]) for condition in all_conditions)

        def add(message: str, insight_type: str) -> None:
            key = (message, insight_type)
            if key in seen:
                return
            seen.add(key)
            insights.append({"message": message, "type": insight_type})

        if temperature < 10:
            add("Cold weather expected, wear warm layers before heading out.", "warning")

        if is_rainy:
            add("Rain likely, carry an umbrella before you leave.", "warning")

        if is_snowy:
            add("Snow advisory: use warm gear and be careful on roads and walkways.", "warning")

        if not insights:
            add("Conditions look stable. Standard outdoor plans should be fine.", "info")

        return insights[: self.MAX_INSIGHTS]

    @staticmethod
    def _contains_any(text: str, keywords: list[str]) -> bool:
        return any(keyword in text for keyword in keywords)
