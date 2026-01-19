import { useState } from 'react';
import { getForecasts } from '../dv/facade/dvFacade';

export function ForecastsPage() {
  const [form, setForm] = useState({ 
    fromDate: "", 
    toDate: "", 
    buildingId: "",
    type: "energy_demand" // Domyślna wartość
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

    const result = await getForecasts(form);
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
      <h1>Data Visualization – Forecasts</h1>

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
            Forecast type: <br/>
            <select name="type" onChange={change} value={form.type}>
                <option value="energy_demand">Energy Demand</option>
                <option value="temp_setpoint">Temperature</option>
                <option value="price">Price</option>
            </select>
        </label>

        <button type="submit" disabled={loading}>
            {loading ? "Loading..." : "Download"}
        </button>
      </form>

      {errors.length > 0 && (
        <ul style={{ color: "red", marginTop: 20 }}>
          {errors.map((e, i) => <li key={i}>{e}</li>)}
        </ul>
      )}

      {data && (
        <div style={{ marginTop: 30, border: '1px solid #ccc', padding: 20, borderRadius: 8 }}>
            <h3>{data.seriesName}</h3>
            <p>Horizon: {data.horizon} | Unit: <strong>{data.unit}</strong></p>

            <div style={{ 
                display: 'flex', gap: '10px', alignItems: 'flex-end', 
                height: 200, overflowX: 'auto', paddingBottom: 10 
            }}>
                {data.values.map((val, i) => (
                    <div key={i} style={{ textAlign: 'center', minWidth: 40 }}>
                        <div style={{ 
                            height: `${Math.min(val * 2, 150)}px`, 
                            background: '#FF9800', 
                            width: '20px', 
                            margin: '0 auto',
                            borderRadius: '3px 3px 0 0',
                            opacity: data.confidence && data.confidence[i] ? data.confidence[i] : 1 
                        }} title={`Wartość: ${val}, Pewność: ${data.confidence?.[i]}`}></div>
                        <div style={{ fontSize: '10px', marginTop: 5, transform: 'rotate(-45deg)', whiteSpace: 'nowrap' }}>
                            {data.labels[i]}
                        </div>
                    </div>
                ))}
            </div>
            {data.confidence && <small style={{color: '#666'}}></small>}
        </div>
      )}
    </div>
  );
}