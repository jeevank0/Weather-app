from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.responses import JSONResponse

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.weather import router as weather_router
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.db.base import init_db

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    load_dotenv(dotenv_path=env_path)
    if not os.getenv("TOMORROW_API_KEY"):
        raise RuntimeError("TOMORROW_API_KEY is not configured")
    init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        message = exc.detail
        if isinstance(message, list) and message:
            first_item = message[0]
            if isinstance(first_item, dict):
                message = first_item.get("msg", "Request failed")
        elif isinstance(message, dict):
            message = message.get("message") or message.get(
                "detail") or "Request failed"
        elif not isinstance(message, str):
            message = "Request failed"

        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "message": str(message)},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        errors = exc.errors()
        message = "Validation error"
        if errors:
            first_error = errors[0]
            message = str(first_error.get("msg", message))
        return JSONResponse(
            status_code=422,
            content={"success": False, "message": message},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, __: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Internal server error"},
        )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        endpoint = request.url.path
        started_at = time.perf_counter()
        try:
            response = await call_next(request)
            elapsed_ms = (time.perf_counter() - started_at) * 1000
            logger.info(
                "API request completed endpoint=%s status=%s duration_ms=%.2f",
                endpoint,
                response.status_code,
                elapsed_ms,
            )
            return response
        except Exception:
            elapsed_ms = (time.perf_counter() - started_at) * 1000
            logger.exception(
                "API request failed endpoint=%s status=500 duration_ms=%.2f",
                endpoint,
                elapsed_ms,
            )
            raise

    app.include_router(health_router, prefix=settings.api_prefix)
    app.include_router(weather_router, prefix=settings.api_prefix)
    return app


app = create_app()
