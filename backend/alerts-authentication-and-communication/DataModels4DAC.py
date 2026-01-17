from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

class Measurement(BaseModel):
    id: str
    device_id: str
    metric: str
    value: float
    timestamp: datetime
    tags: Optional[Dict[str, Any]] = None

class Forecast(BaseModel):
    id: str
    type: str
    horizon: str
    issued_at: datetime
    requested_by: str
    series_item: List[Dict[str, Any]] 
    valid_for: Dict[str, datetime]    
    model_meta: Dict[str, str]       
    scope: Optional[Dict[str, str]] = None

class MeasurementResponse(BaseModel):
    ts: datetime
    value: float
    metric: str
    device_id: str
    buildingId: str 

class ForecastResponse(BaseModel):
    buildingId: str
    type: str
    horizon: str
    series: List[Dict[str, Any]]
    algo: Optional[str] = None

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

class DeviceMetadata(BaseModel):
    id: str
    device_id: str
    type: str
    building_id: str
    room_id: Optional[str] = None
    status: str

class AlertSeverity(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class Alert(BaseModel):
    id: str
    building_id: str
    severity: AlertSeverity
    message: str
    device_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)