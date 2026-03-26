# AI-Powered Weather App

A production-minded full-stack weather platform built with React + Vite on the frontend and FastAPI + SQLAlchemy on the backend.

It delivers real-time weather search, 5-day forecast, history tracking, data exports, and smart integrations (Maps + YouTube), with a clean modular architecture designed to scale from SQLite to PostgreSQL.

## Features

- Weather search by location
- Current weather with humidity and weather condition
- 5-day forecast view
- Browser geolocation with reverse geocoding to city
- Full CRUD for weather history records
- Export history as CSV and JSON
- Google Maps link generation for searched location
- YouTube video integration for travel/weather context
- Clean error handling across backend and frontend

## Tech Stack

### Frontend

- React 18
- Vite 5
- React Router DOM
- Axios
- CSS (responsive, minimal UI)

### Backend

- FastAPI
- SQLAlchemy 2
- Pydantic / pydantic-settings
- Uvicorn
- httpx
- SQLite (default), PostgreSQL-ready structure

## Architecture

The application is split into two clear layers:

- `frontend/`: UI, routing, hooks, and API client abstractions
- `backend/`: API endpoints, service layer, schema validation, and persistence

### Backend design

- `app/api/v1/endpoints`: route handlers and HTTP concerns
- `app/services`: business logic and external API integrations
- `app/schemas`: request/response contracts and input validation
- `app/db`: SQLAlchemy engine, session management, and models
- `app/core`: environment-driven configuration

### Frontend design

- `src/pages`: route-level screens (`Home`, `History`)
- `src/components`: reusable UI building blocks
- `src/hooks`: page-level state and side-effect orchestration
- `src/api`: Axios wrappers and endpoint-specific API functions

This separation keeps the codebase maintainable, testable, and easy to extend.

## Project Structure

```text
weather-ai-app/
  backend/
    app/
      api/v1/endpoints/
      core/
      db/
      schemas/
      services/
    tests/
    requirements.txt
  frontend/
    src/
      api/
      components/
      hooks/
      pages/
      styles/
    package.json
```

## Setup Instructions

### 1. Clone and enter project

```bash
git clone <your-repo-url>
cd weather-ai-app
```

### 2. Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Update `backend/.env` with your keys:

- `TOMORROW_API_KEY`
- `GOOGLE_MAPS_API_KEY` (optional)
- `YOUTUBE_API_KEY` (optional)

Run backend:

```bash
uvicorn app.main:app --reload
```

Backend runs at: `http://localhost:8000`

### 3. Frontend setup

```bash
cd ../frontend
npm install
cp .env.example .env
npm run dev
```

Frontend runs at: `http://localhost:5173`

## API Endpoints

Base URL: `http://localhost:8000/api/v1`

### Weather Intelligence

- `GET /weather/live?location={city}`
  - Returns current weather + 5-day forecast
- `GET /weather/reverse-geocode?lat={lat}&lon={lon}`
  - Converts coordinates into city name
- `GET /weather/extras?location={city}`
  - Returns map URL and YouTube video URL

### Weather History CRUD

- `POST /weather`
  - Create weather history record
- `GET /weather`
  - List all records
- `GET /weather/{id}`
  - Get a single record
- `PUT /weather/{id}`
  - Update record
- `DELETE /weather/{id}`
  - Delete record

### Export

- `GET /weather/export?format=csv`
- `GET /weather/export?format=json`

## Demo Steps

1. Start backend and frontend servers.
2. Open `http://localhost:5173`.
3. On Home page:
   - Allow geolocation permission to auto-fetch local weather, or
   - Search manually by city/location.
4. Verify output includes:
   - temperature
   - humidity
   - weather condition
   - 5-day forecast
5. Navigate to History page:
   - View saved records
   - Edit a record
   - Delete a record
6. Click export buttons:
   - Download CSV
   - Download JSON
7. Optionally test extras endpoint from backend API docs (`/docs`) for map and YouTube links.

## Error Handling Highlights

- Backend validates location and date ranges with clear messages.
- Frontend maps API/network failures to user-friendly messages.
- Geolocation permission/timeouts are handled gracefully in UI.

## Future Enhancements

- Add auth and multi-user history
- Add Redis caching for weather lookups
- Introduce Alembic migration workflow for production DBs
- Add CI pipeline with automated tests and linting
