// This file stores mock data which can be used to test our module with no access to backend

export const rawAlerts = [
  {
    id: 'ALERT-1',
    buildingId: 'B1',
    severity: 'HIGH',
    message: 'Energy usage exceeded threshold',
    timestamp: '2025-01-01T12:30:00Z',
  },
  {
    id: 'ALERT-2',
    buildingId: 'B2',
    severity: 'MEDIUM',
    message: 'Temperature out of range',
    timestamp: '2025-01-02T09:15:00Z',
  },
  {
    id: 'ALERT-3',
    buildingId: 'B3',
    severity: 'LOW',
    message: 'Daily energy usage slightly above the average',
    timestamp: '2025-01-03T07:25:00Z',
  },
];
