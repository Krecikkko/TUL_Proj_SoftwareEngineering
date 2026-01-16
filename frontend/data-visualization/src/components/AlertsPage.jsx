import { useState } from 'react';
import { getAlerts } from '../dv/facade/dvFacade';

export function AlertsPage() {
  const [form, setForm] = useState({ fromDate: "", toDate: "", buildingId: "" });
  const [errors, setErrors] = useState([]);
  const [alerts, setAlerts] = useState([]);

  const change = e => setForm({ ...form, [e.target.name]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    const result = await getAlerts(form);

    if (result.status === "validation-error") {
      setErrors(result.errors);
      setAlerts([]);
    } else {
      setErrors([]);
      setAlerts(result.data);
    }
  }

  return (
    <div style={{ padding: 20 }}>
      <h1>Data Visualization – Alerts</h1>

      <form onSubmit={submit}>
        <p>
          <label>From: <input type="date" name="fromDate" onChange={change}/></label>
        </p>
        <p>
          <label>To: <input type="date" name="toDate" onChange={change}/></label>
        </p>
        <p>
          <label>Building ID (begins with 'B'): <input type="text" name="buildingId" onChange={change}/></label>
        </p>
        <button>Submit</button>
      </form>

      {errors.length > 0 && (
        <ul style={{ color: "red" }}>
          {errors.map(e => <li key={e}>{e}</li>)}
        </ul>
      )}

      {alerts.length > 0 && (
        <table border="1" cellPadding="5">
          <thead>
            <tr>
              <th>ID</th>
              <th>Building</th>
              <th>Severity</th>
              <th>Message</th>
              <th>Time</th>
            </tr>
          </thead>
          <tbody>
            {alerts.map(a => (
              <tr key={a.id}>
                <td>{a.id}</td>
                <td>{a.buildingName}</td>
                <td style={{ color: a.severity.color }}>
                  {a.severity.icon} {a.severity.label}
                </td>
                <td>{a.message}</td>
                <td>{a.time}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
