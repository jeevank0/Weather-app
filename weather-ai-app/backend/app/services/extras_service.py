from urllib.parse import quote_plus


class ExtrasService:
    async def get_location_extras(self, location: str) -> dict[str, str]:
        normalized_location = location.strip()
        if len(normalized_location) < 2:
            raise ValueError(
                "Please provide a valid location with at least 2 characters")

        return {
            "map_url": self._build_map_search_url(normalized_location),
            "youtube_url": self._build_youtube_search_url(normalized_location),
        }

    @staticmethod
    def _build_map_search_url(location: str) -> str:
        return f"https://www.google.com/maps/search/?api=1&query={quote_plus(location)}"

    @staticmethod
    def _build_youtube_search_url(location: str) -> str:
        query = quote_plus(f"{location} weather")
        return f"https://www.youtube.com/results?search_query={query}"
