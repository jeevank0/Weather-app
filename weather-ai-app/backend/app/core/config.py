from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Weather AI Backend"
    app_env: str = "development"
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./weather.db"
    tomorrow_api_key: str = ""
    tomorrow_base_url: str = "https://api.tomorrow.io/v4/weather"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8")


settings = Settings()
