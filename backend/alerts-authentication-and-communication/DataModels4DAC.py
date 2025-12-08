from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

# --- 1. METRICS MODELS (Measurements) ---
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

# --- 2. CORE DB MODELS (Users) ---
# This was missing in your file!
class UserRole(str, Enum):
    ADMIN = "admin"
    MAINTENANCE = "maintenance"
    USER = "user"

class User(BaseModel):
    user_id: str
    username: str
    password_hash: str
    role: UserRole
    full_name: str

# --- 3. FORECAST MODELS ---
# This was also missing!
class ForecastSeriesItem(BaseModel):
    timestamp: datetime = Field(..., alias="ts")
    value: float

class Forecast(BaseModel):
    forecast_id: str = Field(..., alias="_id")
    type: str
    horizon: str
    issued_at: datetime
    series: List[ForecastSeriesItem]

# --- 4. ALERT MODELS ---
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