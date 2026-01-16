from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

# --- 1. DAC INPUT MODELS (Matches DAC Interface) ---
# We use these to READ from the database
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

# --- 2. FRONTEND OUTPUT MODELS (Matches React App) ---
# We use these to SEND to the frontend (Translation Layer)

class MeasurementResponse(BaseModel):
    # React expects 'ts', DAC gives 'timestamp'
    ts: datetime
    value: float
    metric: str
    device_id: str
    buildingId: str # React expects camelCase here

class ForecastResponse(BaseModel):
    # React expects 'series', DAC gives 'series_item'
    buildingId: str
    type: str
    horizon: str
    series: List[Dict[str, Any]]
    algo: Optional[str] = None

# --- 3. CORE MODELS ---
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

# --- 4. ALERT MODELS ---
# UPDATED: Matches 'rawAlerts.js' and 'AlertsPage.jsx'
class AlertSeverity(str, Enum):
    HIGH = "HIGH"      # Red
    MEDIUM = "MEDIUM"  # Orange
    LOW = "LOW"        # Green

class Alert(BaseModel):
    id: str
    building_id: str    # Required for frontend filtering
    severity: AlertSeverity
    message: str
    device_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)