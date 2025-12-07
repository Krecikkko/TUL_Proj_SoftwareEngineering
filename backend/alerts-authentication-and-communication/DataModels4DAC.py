from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

# ... (Keep existing MetricType, MeasurementReading, DeviceStatus classes) ...

# --- EXISTING METRICS MODELS ---
class MetricType(str, Enum):
    POWER = "power_w"
    TEMPERATURE = "temp_c"
    HUMIDITY = "humidity_pct"
    CO2 = "co2_ppm"

class MeasurementReading(BaseModel):
    reading_id: str = Field(..., alias="_id")
    device_id: str
    metric: MetricType
    value: float
    timestamp: datetime = Field(..., alias="ts")
    tags: Optional[Dict[str, Any]] = None

class DeviceStatus(BaseModel):
    device_id: str = Field(..., alias="_id")
    last_state: Dict[str, Any]
    updated_at: datetime

# ... (Keep existing User and Forecast models) ...

# --- NEW: ALERT MODELS ---
class AlertSeverity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"

class Alert(BaseModel):
    alert_id: str
    severity: AlertSeverity
    message: str
    device_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)