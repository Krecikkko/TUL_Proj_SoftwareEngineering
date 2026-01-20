// src/components/DashboardTestPage.jsx
import { useState, useEffect } from 'react';
import { getDashboardStats } from '../dv/facade/dvFacade';

export function DashboardTestPage() {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Funkcja do pobrania danych zaraz po wejściu na stronę
    async function fetchData() {
      console.log("🚀 Calling getDashboardStats...");
      const data = await getDashboardStats("B1"); // Testujemy dla budynku B1
      
      if (data) {
        setStats(data);
      } else {
        setError("Błąd pobierania (lub brak backendu)");
      }
    }
    fetchData();
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h1>Dashboard KPI Test</h1>
      
      {error && <p style={{ color: 'red' }}>Status: {error}</p>}
      
      {!stats && !error && <p>Loading...</p>}

      {stats && (
        <div style={{ display: 'flex', gap: 20, marginTop: 20 }}>
            {/* Kafelki jak w projekcie */}
            <div style={{ border: '1px solid #ccc', padding: 20, borderRadius: 8 }}>
                <h3>Power Usage</h3>
                <p style={{ fontSize: '24px', fontWeight: 'bold', color: 'blue' }}>
                    {stats.current_power_usage} W
                </p>
            </div>

            <div style={{ border: '1px solid #ccc', padding: 20, borderRadius: 8 }}>
                <h3>Avg Temp</h3>
                <p style={{ fontSize: '24px', fontWeight: 'bold', color: 'orange' }}>
                    {stats.temperature_avg} °C
                </p>
            </div>

            <div style={{ border: '1px solid #ccc', padding: 20, borderRadius: 8 }}>
                <h3>Alerts</h3>
                <p style={{ fontSize: '24px', fontWeight: 'bold', color: 'red' }}>
                    {stats.active_alerts_count}
                </p>
            </div>
        </div>
      )}
      
      {stats && (
          <div style={{ marginTop: 20, padding: 10, background: '#f0f0f0' }}>
              <strong>Forecast Summary:</strong> {stats.forecast_summary}
          </div>
      )}
    </div>
  );
}