import { deleteJson, getFile, getJson, putJson } from './httpClient';
import { formatLocationName } from '../utils/locationFormat';

function normalizeInsight(item) {
  if (!item || typeof item !== 'object') return null;
  const message = typeof item.message === 'string' ? item.message.trim() : '';
  if (!message) return null;

  const type = item.type === 'alert' || item.type === 'warning' || item.type === 'info' ? item.type : 'info';
  return { message, type };
}

function normalizeForecastDay(item) {
  if (!item || typeof item !== 'object') return null;
  if (!item.date) return null;

  return {
    date: item.date,
    temperature: Number(item.temperature ?? 0),
    humidity: Number(item.humidity ?? 0),
    weather_condition: typeof item.weather_condition === 'string' ? item.weather_condition : 'Unknown',
  };
}

function normalizeHourlyPoint(item) {
  if (!item || typeof item !== 'object') return null;
  if (!item.time) return null;

  return {
    time: item.time,
    temperature: Number(item.temperature ?? 0),
    weather_condition: typeof item.weather_condition === 'string' ? item.weather_condition : 'Unknown',
  };
}

function normalizeLiveWeather(data) {
  if (!data || typeof data !== 'object') {
    throw new Error('Invalid weather payload');
  }

  return {
    location:
      typeof data.location === 'string' && data.location.trim()
        ? formatLocationName(data.location.trim())
        : 'Unknown location',
    temperature: Number(data.temperature ?? 0),
    humidity: Number(data.humidity ?? 0),
    weather_condition: typeof data.weather_condition === 'string' ? data.weather_condition : 'Unknown',
    map_url: typeof data.map_url === 'string' ? data.map_url : '',
    youtube_url: typeof data.youtube_url === 'string' ? data.youtube_url : '',
    forecast_list: Array.isArray(data.forecast_list) ? data.forecast_list.map(normalizeForecastDay).filter(Boolean) : [],
    hourly_forecast: Array.isArray(data.hourly_forecast) ? data.hourly_forecast.map(normalizeHourlyPoint).filter(Boolean) : [],
    insights: Array.isArray(data.insights) ? data.insights.map(normalizeInsight).filter(Boolean) : [],
  };
}

function extractFilenameFromDisposition(contentDisposition, fallbackName) {
  if (!contentDisposition) return fallbackName;
  const match = contentDisposition.match(/filename="?([^";]+)"?/i);
  return match?.[1] || fallbackName;
}

export async function getWeather(location) {
  const response = await getJson('/weather/live', { location: location.trim() });
  return normalizeLiveWeather(response.data);
}

export async function getWeatherByCoordinates(lat, lon) {
  const response = await getJson('/weather/live', { lat, lon });
  return normalizeLiveWeather(response.data);
}

export async function fetchCityFromCoordinates(lat, lon) {
  const response = await getJson('/weather/reverse-geocode', { lat, lon });
  return response.data.city;
}

export async function getWeatherHistory() {
  const response = await getJson('/weather');
  return response.data;
}

export async function updateWeather(recordId, payload) {
  const response = await putJson(`/weather/${recordId}`, payload);
  return response.data;
}

export async function deleteWeather(recordId) {
  return deleteJson(`/weather/${recordId}`);
}

export async function exportWeather(format) {
  const selectedFormat = format === 'csv' ? 'csv' : 'json';
  const fallback = selectedFormat === 'csv' ? 'weather_export.csv' : 'weather_export.json';

  const { blob, headers } = await getFile('/weather/export', { format: selectedFormat });
  const filename = extractFilenameFromDisposition(headers['content-disposition'], fallback);
  return { blob, filename };
}

// Backward-compatible aliases used by existing hooks/components.
export const fetchLiveWeather = getWeather;
export const fetchLiveWeatherByCoordinates = getWeatherByCoordinates;
export const fetchWeatherHistory = getWeatherHistory;
export const updateWeatherRecord = updateWeather;
export const deleteWeatherRecord = deleteWeather;
export const exportWeatherData = exportWeather;
