from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

# --- 1. MEASUREMENT MODELS ---
# Matches DAC 'Measurement' Document
class MeasurementReading(BaseModel):
    id: Optional[str] = Field(None, alias="_id") # Beanie adds this automatically
    deviceId: str
    metric: str
    value: float
    ts: datetime
    tags: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True

# --- 2. FORECAST MODELS ---
# Matches DAC 'Forecast' Document
class Forecast(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    type: str               # "energy_demand", "price"
    horizon: str            # "1H", "1D"
    issued_at: datetime
    requested_by: str       # UUID
    series_item: List[Dict[str, Any]] # [{ts, value, conf}, ...]
    valid_for: Dict[str, datetime]    # {from, to}
    model_meta: Dict[str, str]        # {algo, ver}
    scope: Optional[Dict[str, str]] = None

# --- 3. CORE MODELS ---
# Matches DAC 'User' Document
class UserRole(str, Enum):
    ADMIN = "admin"
    MAINTENANCE = "maintenance"
    USER = "user"

class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    username: str
    password_hash: str
    role: UserRole = UserRole.USER
    full_name: str
    email: Optional[str] = None

# Matches DAC 'Device' Document (Metadata)
class DeviceMetadata(BaseModel):
    device_id: str
    building_id: str
    room_id: Optional[str] = None
    type: str
    status: str

# --- 4. ALERT MODELS (AAC Specific) ---
# These remain yours, but references must match DAC IDs
class AlertSeverity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"

class Alert(BaseModel):
    alert_id: str
    severity: AlertSeverity
    message: str
    device_id: Optional[str] = None # Reference to DAC 'deviceId'
    timestamp: datetime = Field(default_factory=datetime.utcnow)