from beanie import Document
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Optional, Any

class Forecast(Document):
    type: str               # "energy_demand", "price", etc.
    horizon: str            # "1H", "1D"
    issued_at: datetime
    requested_by: str       # UUID string
    series_item: List[Dict[str, Any]] # [{ts, value, conf}, ...]
    valid_for: Dict[str, datetime]    # {from, to}
    model_meta: Dict[str, str]        # {algo, ver}
    scope: Optional[Dict[str, str]] = None 
    
    class Settings:
        name = "Forecasts"