from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

# Based on Source 397: "metric: power_w | temp_c | humidity_pct | co2_ppm"
class MetricType(str, Enum):
    POWER = "power_w"
    TEMPERATURE = "temp_c"
    HUMIDITY = "humidity_pct"
    CO2 = "co2_ppm"

# Based on Source 397: "MEASUREMENTS" Table
class MeasurementReading(BaseModel):
    reading_id: str = Field(..., alias="_id")  # Maps to Mongo ObjectId
    device_id: str
    metric: MetricType
    value: float
    timestamp: datetime = Field(..., alias="ts")
    tags: Optional[Dict[str, Any]] = None # e.g., {"room": "A-101"}

# Based on Source 398: "DEVICE_STATUS" Table
class DeviceStatus(BaseModel):
    device_id: str = Field(..., alias="_id") # "Unique per collection"
    last_state: Dict[str, Any] # e.g., { "temp_set": 21.5, "on": true }
    updated_at: datetime