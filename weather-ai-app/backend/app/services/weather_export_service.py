import csv
import io
import json
from datetime import date, datetime
from typing import Any

from app.db.models.weather_request import WeatherRequest


class WeatherExportService:
    def build_csv_content(self, records: list[WeatherRequest]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "location", "start_date",
                        "end_date", "temperature", "created_at"])

        for record in records:
            writer.writerow(
                [
                    record.id,
                    record.location,
                    self._serialize_value(record.start_date),
                    self._serialize_value(record.end_date),
                    record.temperature,
                    self._serialize_value(record.created_at),
                ]
            )

        return output.getvalue()

    def build_json_content(self, records: list[WeatherRequest]) -> str:
        payload = [
            {
                "id": record.id,
                "location": record.location,
                "start_date": self._serialize_value(record.start_date),
                "end_date": self._serialize_value(record.end_date),
                "temperature": record.temperature,
                "created_at": self._serialize_value(record.created_at),
            }
            for record in records
        ]
        return json.dumps(payload, indent=2)

    @staticmethod
    def _serialize_value(value: Any) -> str:
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        return str(value)
