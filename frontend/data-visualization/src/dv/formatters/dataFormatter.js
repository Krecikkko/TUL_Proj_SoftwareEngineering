export function formatAlerts(rawAlerts) {
  if (!Array.isArray(rawAlerts)) return [];

  return rawAlerts.map(alert => {
    let severityConfig = { label: 'Unknown', color: 'gray', icon: '?' };
    const severityValue = typeof alert.severity === 'string' ? alert.severity : alert.severity?.label;

    if (severityValue === 'CRITICAL' || severityValue === 'critical') {
      severityConfig = { label: 'CRITICAL', color: 'red', icon: '!!' };
    } else if (severityValue === 'WARNING' || severityValue === 'warning') {
      severityConfig = { label: 'WARNING', color: 'orange', icon: '!' };
    }

    return {
      id: alert.alert_id || alert.id,
      buildingName: alert.building_id || "Building-1",
      severity: severityConfig,
      message: alert.message,
      time: alert.timestamp || alert.time
    };
  });
}

export function formatMeasurements(rawData, meta) {
  if (!Array.isArray(rawData) || rawData.length === 0) return null;
  
  const first = rawData[0];
  const unitMap = {
      "temp_c": "°C",
      "power_w": "W",
      "co2_ppm": "ppm",
      "humidity_pct": "%"
  };

  const values = rawData.map(m => m.value);
  const labels = rawData.map(m => {
      const ts = m.timestamp || m.ts;
      return ts ? new Date(ts).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : "";
  });

  return {
    seriesName: `Metric: ${first.metric}`,
    unit: unitMap[first.metric] || '',
    values: values,
    labels: labels
  };
}

// --- POPRAWIONA FUNKCJA (Forecasts) ---
export function formatForecasts(rawData, meta) {
  // Sprawdzamy, czy otrzymaliśmy obiekt prognozy z serią danych
  if (!rawData || !rawData.series || !Array.isArray(rawData.series)) {
      return null;
  }
  
  // Wyciągamy wartości i etykiety czasowe do osobnych tablic
  const values = rawData.series.map(point => point.value);
  const labels = rawData.series.map(point => {
      const ts = point.timestamp || point.ts;
      // Formatujemy datę (np. "14:00")
      return ts ? new Date(ts).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : "";
  });

  // Skalujemy wartości, aby wykres był czytelny (backend wysyła duże liczby, np. 3000 kW)
  // W realnej aplikacji lepiej skalować to dynamicznie w komponencie widoku,
  // ale tutaj dla uproszczenia zwracamy surowe wartości, a widok ma swoje skalowanie.
  
  return {
      seriesName: `Forecast: ${rawData.type || 'Unknown'}`,
      horizon: rawData.horizon || '24h',
      unit: "kW", // Mock generuje "energy_demand", więc kW
      values: values,
      labels: labels,
      confidence: [] // Mock nie generuje pewności, zostawiamy puste
  };
}