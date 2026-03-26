import { useState } from 'react';
import { fetchLiveWeather, fetchLiveWeatherByCoordinates } from '../services/weatherService';
import { formatLocationName } from '../utils/locationFormat';

export function useLiveWeather() {
  const locationNotFoundMessage = 'City not found. Please try again.';
  const genericFetchMessage = 'Unable to fetch weather data.';

  const resolveErrorMessage = (error, fallbackMessage) => {
    const rawMessage = error instanceof Error && typeof error.message === 'string' ? error.message.toLowerCase() : '';

    if (rawMessage.includes('city') || rawMessage.includes('location') || rawMessage.includes('not found')) {
      return locationNotFoundMessage;
    }

    if (rawMessage) {
      return genericFetchMessage;
    }

    return fallbackMessage;
  };

  const isValidWeatherPayload = (data) => {
    return Boolean(
      data &&
        typeof data === 'object' &&
        typeof data.location === 'string' &&
        typeof data.temperature !== 'undefined' &&
        typeof data.humidity !== 'undefined'
    );
  };

  const [weather, setWeather] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isLocating, setIsLocating] = useState(false);
  const [resolvedLocation, setResolvedLocation] = useState('');
  const [error, setError] = useState('');

  const searchWeather = async (location, options = {}) => {
    if (!location || !location.trim()) {
      setError('Please enter a valid location');
      return;
    }

    setIsLoading(true);
    setError('');
    setResolvedLocation(formatLocationName(location.trim()));

    try {
      const data = await fetchLiveWeather(location);
      if (!isValidWeatherPayload(data)) {
        throw new Error('Invalid weather payload');
      }
      setWeather(data);
    } catch (err) {
      setWeather(null);
      setError(resolveErrorMessage(err, options.apiFailureMessage || genericFetchMessage));
    } finally {
      setIsLoading(false);
    }
  };

  const resolveDisplayLocation = async (lat, lon) => {
    const fallback = `${lat.toFixed(4)},${lon.toFixed(4)}`;

    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(
          lon
        )}&format=json`
      );

      if (!response.ok) return fallback;

      const payload = await response.json();
      const address = payload?.address || {};
      const displayCity = address.city || address.town || address.village || address.suburb;

      if (typeof displayCity === 'string' && displayCity.trim()) {
        return displayCity.trim();
      }
    } catch {
      return fallback;
    }

    return fallback;
  };

  const fetchWeatherByCurrentLocation = async () => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by this browser.');
      return;
    }

    setIsLocating(true);
    setError('');

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;

        try {
          setIsLoading(true);
          const data = await fetchLiveWeatherByCoordinates(latitude, longitude);
          if (!isValidWeatherPayload(data)) {
            throw new Error('Invalid weather payload');
          }
          const displayLocation = await resolveDisplayLocation(latitude, longitude);
          setWeather(data);
          setResolvedLocation(formatLocationName(displayLocation));
          setError('');
        } catch (err) {
          setError(resolveErrorMessage(err, genericFetchMessage));
          setWeather(null);
        } finally {
          setIsLoading(false);
          setIsLocating(false);
        }
      },
      (geoError) => {
        setIsLocating(false);
        if (geoError.code === 1) {
          setError('Location access denied. Please allow access or search manually');
          return;
        }
        if (geoError.code === 2) {
          setError('Unable to detect your location. Please check device location services.');
          return;
        }
        if (geoError.code === 3) {
          setError('Location request timed out. Please try again.');
          return;
        }
        setError('Unable to fetch current location. Please search manually.');
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 300000 }
    );
  };

  return {
    weather,
    isLoading,
    isLocating,
    resolvedLocation,
    error,
    searchWeather,
    fetchWeatherByCurrentLocation,
  };
}
