import axios from 'axios';
import { API_BASE_URL } from '../config/env';

const httpClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

function parseApiError(error) {
  const genericMessage = 'Unable to fetch weather data.';
  const cityNotFoundMessage = 'City not found. Please try again.';
  const rateLimitMessage = 'Weather service is busy right now. Please try again in a minute.';

  if (error.code === 'ECONNABORTED') return genericMessage;
  if (!error.response) return genericMessage;

  const status = error.response.status;
  let detail = error.response.data?.message || error.response.data?.detail;

  if (!detail && typeof error.response.data === 'string') {
    detail = error.response.data;
  }

  const detailText = typeof detail === 'string' ? detail.toLowerCase() : '';
  const looksLikeLocationError =
    detailText.includes('location') ||
    detailText.includes('city') ||
    detailText.includes('weather data found') ||
    detailText.includes('forecast not found');
  const looksLikeRateLimit =
    detailText.includes('rate limit') ||
    detailText.includes('request limit') ||
    detailText.includes('too many requests');

  if (status === 404 && looksLikeLocationError) return cityNotFoundMessage;
  if (status === 422 && looksLikeLocationError) return cityNotFoundMessage;
  if (status === 429 || looksLikeRateLimit) return rateLimitMessage;

  if (status >= 500 && typeof detail === 'string' && detail.trim()) {
    return detail;
  }

  return genericMessage;
}

export async function getJson(path, params = {}) {
  try {
    const response = await httpClient.get(path, { params });
    if (response.data?.success === false) {
      throw new Error(response.data?.message || 'Something went wrong, try again');
    }
    return response.data;
  } catch (error) {
    if (error instanceof Error && !error.response) {
      throw error;
    }
    throw new Error(parseApiError(error));
  }
}

export async function putJson(path, body) {
  try {
    const response = await httpClient.put(path, body);
    if (response.data?.success === false) {
      throw new Error(response.data?.message || 'Something went wrong, try again');
    }
    return response.data;
  } catch (error) {
    if (error instanceof Error && !error.response) {
      throw error;
    }
    throw new Error(parseApiError(error));
  }
}

export async function deleteJson(path) {
  try {
    const response = await httpClient.delete(path);
    if (response.data?.success === false) {
      throw new Error(response.data?.message || 'Something went wrong, try again');
    }
    return response.data;
  } catch (error) {
    if (error instanceof Error && !error.response) {
      throw error;
    }
    throw new Error(parseApiError(error));
  }
}

export async function getFile(path, params = {}) {
  try {
    const response = await httpClient.get(path, {
      params,
      responseType: 'blob',
    });
    return {
      blob: response.data,
      headers: response.headers,
    };
  } catch (error) {
    throw new Error(parseApiError(error));
  }
}
