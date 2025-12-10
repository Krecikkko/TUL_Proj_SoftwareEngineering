from beanie import Document
from datetime import datetime
from typing import Dict, Any, Optional

class Measurement(Document):
    deviceId: str
    metric: str
    value: float
    ts: datetime
    tags: Optional[Dict[str, Any]] = None
    
    class Settings:
        name = "Measurements"