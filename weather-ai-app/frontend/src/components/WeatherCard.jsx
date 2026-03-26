import AIInsights from './AIInsights';
import { formatLocationName } from '../utils/locationFormat';

function WeatherCard({ weather, displayLocation = '' }) {
  const hasWeather = Boolean(weather && typeof weather === 'object');
  const weatherData = hasWeather ? weather : {};

  const safeForecastList = Array.isArray(weatherData.forecast_list)
    ? weatherData.forecast_list.filter((day) => day && typeof day === 'object' && day.date)
    : [];
  const safeHourlyForecast = Array.isArray(weatherData.hourly_forecast)
    ? weatherData.hourly_forecast.filter((hour) => hour && typeof hour === 'object' && hour.time)
    : [];

  const toLocalDateKey = (value) => {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return '';

    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  const todayKey = toLocalDateKey(new Date());
  const todayHourlyForecast = safeHourlyForecast
    .filter((hour) => toLocalDateKey(hour.time) === todayKey)
    .sort((a, b) => new Date(a.time) - new Date(b.time))
    .slice(0, 24);

  const readableLocation = formatLocationName((displayLocation || '').trim() || weatherData.location || '');

  const formatForecastDate = (dateValue) => {
    const parsed = new Date(`${dateValue}T00:00:00`);
    if (Number.isNaN(parsed.getTime())) return dateValue;

    return parsed.toLocaleDateString(undefined, {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
    });
  };

  const getConditionIcon = (condition) => {
    const value = (condition || '').toLowerCase();
    if (value.includes('thunder')) return '⛈️';
    if (value.includes('rain') || value.includes('drizzle')) return '🌧️';
    if (value.includes('snow')) return '❄️';
    if (value.includes('cloud')) return '☁️';
    if (value.includes('mist') || value.includes('fog') || value.includes('haze')) return '🌫️';
    if (value.includes('clear') || value.includes('sun')) return '☀️';
    return '🌤️';
  };

  const formatHourlyTime = (timeValue) => {
    const parsed = new Date(timeValue);
    if (Number.isNaN(parsed.getTime())) return timeValue;

    return parsed.toLocaleTimeString(undefined, {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    });
  };

  if (!hasWeather) return null;

  return (
    <section className="weather-layout" aria-live="polite">
      <article className="panel-card current-card">
        <h3>{readableLocation}</h3>
        <p className="temperature">{Number(weatherData.temperature ?? 0).toFixed(1)}°C</p>
        <p className="condition">{weatherData.weather_condition}</p>
        <p className="humidity">Humidity: {Number(weatherData.humidity ?? 0)}%</p>
        <div className="weather-links">
          {weatherData.map_url && (
            <a href={weatherData.map_url} target="_blank" rel="noreferrer" className="weather-link">
              Open in Maps
            </a>
          )}
          {weatherData.youtube_url && (
            <a href={weatherData.youtube_url} target="_blank" rel="noreferrer" className="weather-link">
              YouTube Weather
            </a>
          )}
        </div>
      </article>

      <AIInsights insights={weatherData.insights} />

      {!!todayHourlyForecast.length && (
        <article className="panel-card hourly-wrap">
          <h4>Hourly Forecast (Today)</h4>
          <ul className="hourly-container" aria-label="Hourly forecast">
            {todayHourlyForecast.map((hour, index) => (
              <li key={`${hour.time}-${index}`} className="hour-card">
                <p className="hourly-time">{formatHourlyTime(hour.time)}</p>
                <p className="hourly-condition" aria-label={hour.weather_condition} title={hour.weather_condition}>
                  <span aria-hidden="true">{getConditionIcon(hour.weather_condition)}</span>
                </p>
                <p className="hourly-temp">{Number(hour.temperature ?? 0).toFixed(1)}°C</p>
              </li>
            ))}
          </ul>
        </article>
      )}

      {!!safeForecastList.length && (
        <article className="panel-card forecast-wrap">
          <h4>5-Day Forecast</h4>
          <ul className="forecast-list">
            {safeForecastList.map((day, index) => (
              <li key={`${day.date}-${index}`}>
                <p className="forecast-date">{formatForecastDate(day.date)}</p>
                <p className="forecast-temp">{Number(day.temperature ?? 0).toFixed(1)}°C</p>
                <p className="forecast-condition">
                  <span aria-hidden="true">{getConditionIcon(day.weather_condition)}</span>
                  <span>{day.weather_condition}</span>
                </p>
                <p className="forecast-humidity">Humidity: {Number(day.humidity ?? 0)}%</p>
              </li>
            ))}
          </ul>
        </article>
      )}
    </section>
  );
}

export default WeatherCard;
