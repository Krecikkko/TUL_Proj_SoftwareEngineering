import { rawMetadata } from '../mock_data/rawMetadata';

export function formatAlerts(rawAlerts) {
  return rawAlerts.map(alert => {
    const building = rawMetadata.buildings[alert.buildingId];
    const sev = rawMetadata.severityConfig[alert.severity];

    return {
      id: alert.id,
      buildingName: building?.name ?? alert.buildingId,
      message: alert.message,
      time: new Date(alert.timestamp).toLocaleString(),
      severity: {
        code: alert.severity,
        label: sev?.label ?? alert.severity,
        icon: sev?.icon ?? 'ℹ️',
        color: sev?.color ?? 'gray',
      },
    };
  });
}
