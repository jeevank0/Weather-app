import { Link } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';
import SearchBar from '../components/SearchBar';
import WeatherCard from '../components/WeatherCard';
import { useLiveWeather } from '../hooks/useLiveWeather';

function HomePage() {
  const { weather, isLoading, isLocating, error, resolvedLocation, searchWeather, fetchWeatherByCurrentLocation } = useLiveWeather();

  return (
    <main className="page">
      <section className="container">
        <h2>Live Weather</h2>
        <p className="subtitle">Search any location to view current weather and a 5-day forecast.</p>
        <SearchBar onSearch={searchWeather} isLoading={isLoading} />
        <div className="quick-nav" aria-label="Page navigation">
          <Link to="/history" className="quick-nav-link">
            View History
          </Link>
        </div>
        <button className="secondary-button" type="button" onClick={fetchWeatherByCurrentLocation} disabled={isLocating || isLoading}>
          {isLocating ? 'Fetching your location...' : 'Use Current Location'}
        </button>
        {(isLoading || isLocating) && (
          <LoadingSpinner label={isLocating ? 'Detecting your location...' : 'Loading weather...'} />
        )}
        {error && <p className="error">{error}</p>}
        {!isLoading && !isLocating && !error && !weather && (
          <section className="home-empty-state empty-state" aria-live="polite">
            <span className="empty-state-icon" aria-hidden="true">
              ☁️
            </span>
            <p>Enter a location to get real-time weather insights.</p>
          </section>
        )}
        <WeatherCard weather={weather} displayLocation={resolvedLocation} />
      </section>
    </main>
  );
}

export default HomePage;
