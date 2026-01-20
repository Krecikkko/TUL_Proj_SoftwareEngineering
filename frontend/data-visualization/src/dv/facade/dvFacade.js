import { validate, normalize } from '../validators/inputValidator';
import { formatAlerts, formatForecasts, formatMeasurements } from '../formatters/dataFormatter';

const API_BASE_URL = "http://127.0.0.1:8001/api/v1/gateway";

function getAuthHeaders() {
  const token = localStorage.getItem('access_token');
  return {
    'Authorization': `Bearer ${token}`,
    'Content-type': 'application/json'
  }
}

// --- LOGIN ---
export async function loginUser(username, password) {
  try {
    const response = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      headers: {
        'Content-type': 'application/json',
      },
      body: JSON.stringify({
        username: username,
        password: password
      })
    });
    if(!response.ok) {
      return { status: 'error', message: 'Invalid credentials'};
    }
    const data = await response.json();

    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('userRole', data.role);

    return { status: 'ok', role: data.role};
  }
  catch (error) {
    console.error("Login error:", error);
    return {status: 'error', message: 'Server connection failed'};
  }
}

// --- ALERTS ---
async function fetchAlertsFromAAC(query) {
  try {
    const url = new URL(`${API_BASE_URL}/alerts`);
    url.searchParams.append("buildingId", query.buildingId || "Building-1");
    url.searchParams.append("fromDate", query.timeRange?.from || new Date(Date.now() - 86400000).toISOString());
    url.searchParams.append("toDate", query.timeRange?.to || new Date().toISOString());
    const response = await fetch(url, {headers: getAuthHeaders()});
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
    const url = new URL(`${API_BASE_URL}/measurements`);
    
    // Dodajemy parametry wymagane przez backend
    url.searchParams.append("buildingId", query.buildingId || "Building-1");
    
    const from = query.fromDate ?? query.timeRange?.from ?? new Date(Date.now() - 86400000).toISOString();

  const to = query.toDate ?? query.timeRange?.to ??new Date().toISOString();

    url.searchParams.append("fromDate", from);
    url.searchParams.append("toDate", to);

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

    const response = await fetch(url, {headers: getAuthHeaders()});
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
  
  //const meta = rawMetadata;
  const formatted = formatMeasurements(rawData);
  return {status: 'ok', data: formatted};
}

// --- FORECASTS ---
async function fetchForecasts(query) {
  try {
    const url = new URL(`${API_BASE_URL}/forecasts`);
    url.searchParams.append("buildingId", query.buildingId || "Building-1");
    
	  if (query.timeRange?.from) {
        url.searchParams.append("fromDate", query.timeRange.from); 
    }
    if (query.timeRange?.to) {
        url.searchParams.append("toDate", query.timeRange.to);
    }
    url.searchParams.append("type", query.type || "energy_demand");

    const response = await fetch(url, {headers: getAuthHeaders()});
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
  
  // const meta = rawMetadata;
  const formatted = formatForecasts(rawData);
  return {status: 'ok', data: formatted};
}

// --- DASHBOARD ---
export async function getDashboardStats(buildingId = "Building-1") {
  try {
    const url = new URL(`${API_BASE_URL}/dashboard`);
    url.searchParams.append("buildingId", buildingId);

    const response = await fetch(url, {headers: getAuthHeaders()});

    if(!response.ok) return null;
    return await response.json();
  }
  catch (e) {
    console.error("Dashboard stats error", e);
    return null
  }
}