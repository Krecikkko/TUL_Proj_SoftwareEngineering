import { validate, normalize } from '../validators/inputValidator';
import { formatAlerts } from '../formatters/dataFormatter';
import { rawAlerts } from '../mock_data/rawAlerts';

async function fetchAlertsFromAAC(query) {
  console.log("Simulation of query to AAC:", query);
  const filtered = rawAlerts.filter(a => a.buildingId === query.buildingId);
  return filtered;
}

export async function getAlerts(inputParams) {
  const validation = validate(inputParams);
  if (!validation.ok) {
    return { status: 'validation-error', errors: validation.errors };
  }

  const query = normalize(inputParams);
  const raw = await fetchAlertsFromAAC(query);
  const formatted = formatAlerts(raw);

  return {
    status: 'ok',
    data: formatted,
  };
}
