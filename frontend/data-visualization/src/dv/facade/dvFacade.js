import { validate, normalize } from '../validators/inputValidator';
import { formatAlerts, formatForecasts, formatMeasurements } from '../formatters/dataFormatter';
import { rawMetadata } from '../mock_data/rawMetadata';

const API_BASE_URL = "http://127.0.0.1:8000/api/v1/gateway";

function getAuthToken() {
  return localStorage.getItem('access_token') || "token_for_user"; 
}

// --- ALERTS ---
async function fetchAlertsFromAAC(query) {
  try {
    const token = getAuthToken();
    const url = new URL(`${API_BASE_URL}/alerts`);
    url.searchParams.append("token", token);
    
    const response = await fetch(url);
    if (!response.ok) return [];
    return await response.json();
  } catch (error) {
    console.error("Błąd połączenia z AAC (Alerts):", error);
    return [];
  }
}

export async function getAlerts(inputParams) {
  const validation = validate(inputParams);
  if (!validation.ok) return { status: 'validation-error', errors: validation.errors };

  const query = normalize(inputParams);
  const raw = await fetchAlertsFromAAC(query);
  const formatted = formatAlerts(raw);

  return { status: 'ok', data: formatted };
}

// --- MEASUREMENTS ---
async function fetchMeasurements(query) {
  try {
    const token = getAuthToken();
    const url = new URL(`${API_BASE_URL}/measurements`);
    
    // Dodajemy parametry wymagane przez backend
    url.searchParams.append("token", token);
    url.searchParams.append("buildingId", query.buildingId || "Building-1");
    
    const from = query.fromDate ?? "2026-01-01T00:00:00";
    const to   = query.toDate   ?? "2026-01-30T23:59:59";
    url.searchParams.append("start", from);
    url.searchParams.append("end", to);

    // Mapowanie nazw metryk (Frontend -> Backend)
    const metricMap = {
        "temperature": "temp_c",
        "power": "power_w",
        "co2": "co2_ppm",
        "humidity": "humidity_pct"
    };
    
    // Jeśli użytkownik nie podał metryki, domyślnie 'temp_c'
    const metricName = query.metric ? (metricMap[query.metric] || query.metric) : "temp_c";
    url.searchParams.append("metric", metricName);

    if (query.deviceId) {
        url.searchParams.append("deviceId", query.deviceId);
    }

    const response = await fetch(url);
    if (!response.ok) {
        console.error("Błąd API Measurements:", response.status);
        return [];
    }
    return await response.json();
  } catch (error) {
    console.error("Błąd połączenia z AAC (Measurements):", error);
    return [];
  }
}

export async function getMeasurements(inputParams) {
  const validation = validate(inputParams);
  if(!validation.ok) return {status: 'validation-error', errors: validation.errors};

  const normalizedParams = normalize(inputParams);
  const query = { ...normalizedParams, metric: inputParams.metric, deviceId: inputParams.deviceId };
  
  const rawData = await fetchMeasurements(query);
  
  if(!rawData || rawData.length === 0) {
    return { status: 'no-data', message: "No measurements found"};
  }
  
  const meta = rawMetadata;
  const formatted = formatMeasurements(rawData, meta);
  return {status: 'ok', data: formatted};
}

// --- FORECASTS ---
async function fetchForecasts(query) {
  try {
    const token = getAuthToken();
    const url = new URL(`${API_BASE_URL}/forecasts`);
    url.searchParams.append("token", token);
    url.searchParams.append("buildingId", query.buildingId || "Building-1");
    
	  if (query.fromDate) {
        url.searchParams.append("start", query.fromDate); 
    }
    if (query.toDate) {
        url.searchParams.append("end", query.toDate);
    }
    url.searchParams.append("type", query.type || "temperature");

    
    const response = await fetch(url);
    if (!response.ok) return null;
    
    return await response.json();
  } catch (error) {
    console.error("Błąd połączenia z AAC (Forecasts):", error);
    return null;
  }
}

export async function getForecasts(inputParams) {
  const validation = validate(inputParams);
  if(!validation.ok) return {status: 'validation-error', errors: validation.errors};

  const normalizedParams = normalize(inputParams);
  const query = { ...normalizedParams, type: inputParams.type };
  
  const rawData = await fetchForecasts(query);
  if(!rawData) {
    return { status: 'no-data', message: "No forecasts found"};
  }
  
  const meta = rawMetadata;
  const formatted = formatForecasts(rawData, meta);
  return {status: 'ok', data: formatted};
}