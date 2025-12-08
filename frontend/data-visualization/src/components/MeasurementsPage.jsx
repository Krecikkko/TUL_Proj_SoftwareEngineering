import { useState } from 'react';
import { getMeasurements } from '../dv/facade/dvFacade';

export function MeasurementsPage() {
  const [form, setForm] = useState({ 
    fromDate: "", 
    toDate: "", 
    buildingId: "",
    metric: "temperature", // Domyślna wartość
    deviceId: "" 
  });
  const [errors, setErrors] = useState([]);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const change = e => setForm({ ...form, [e.target.name]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setLoading(true);
    setErrors([]);
    setData(null);

    const result = await getMeasurements(form);
    setLoading(false);

    if (result.status === "validation-error") {
      setErrors(result.errors);
    } else if (result.status === "no-data") {
      setErrors([result.message]);
    } else if (result.status === "ok") {
      setData(result.data);
    } else {
      setErrors(["Unknown error occurred"]);
    }
  }

  return (
    <div style={{ padding: 20 }}>
      <h1>Data Visualization – Measurements</h1>

      <form onSubmit={submit} style={{ display: 'flex', flexWrap: 'wrap', gap: '15px', alignItems: 'flex-end' }}>
        <label>
            From: <br/>
            <input type="date" name="fromDate" onChange={change} required />
        </label>
        
        <label>
            To: <br/>
            <input type="date" name="toDate" onChange={change} required />
        </label>
        
        <label>
            Building ID (eg. B1): <br/>
            <input type="text" name="buildingId" onChange={change} style={{ width: '80px' }} />
        </label>

        <label>
            Metric: <br/>
            <select name="metric" onChange={change} value={form.metric}>
                <option value="temperature">Temperature</option>
                <option value="power">Power</option>
                <option value="humidity">Humidity</option>
                <option value="co2">CO2</option>
            </select>
        </label>

        <label>
            Device ID (Optional): <br/>
            <input type="text" name="deviceId" onChange={change} placeholder="eg. dev_temp_001" />
        </label>

        <button type="submit" disabled={loading}>
            {loading ? "Loading..." : "Download"}
        </button>
      </form>

      {/* Wyświetlanie błędów */}
      {errors.length > 0 && (
        <ul style={{ color: "red", marginTop: 20 }}>
          {errors.map((e, i) => <li key={i}>{e}</li>)}
        </ul>
      )}

      {/* Wyświetlanie danych (Wykres) */}
      {data && (
        <div style={{ marginTop: 30, border: '1px solid #ccc', padding: 20, borderRadius: 8 }}>
            <h3>{data.seriesName}</h3>
            <p>Unit: <strong>{data.unit}</strong></p>

            <div style={{ 
                display: 'flex', gap: '10px', alignItems: 'flex-end', 
                height: 200, overflowX: 'auto', paddingBottom: 10 
            }}>
                {data.values.map((val, i) => (
                    <div key={i} style={{ textAlign: 'center', minWidth: 40 }}>
                        <div style={{ 
                            height: `${Math.min(val * 3, 150)}px`, // Proste skalowanie słupka
                            background: '#4CAF50', 
                            width: '20px', 
                            margin: '0 auto',
                            borderRadius: '3px 3px 0 0'
                        }} title={val}></div>
                        <div style={{ fontSize: '10px', marginTop: 5, transform: 'rotate(-45deg)', whiteSpace: 'nowrap' }}>
                            {data.labels[i]}
                        </div>
                    </div>
                ))}
            </div>
        </div>
      )}
    </div>
  );
}