from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import random
from typing import Optional
from DataModels4DAC import Forecast

class IForecastRead(ABC):
    # Matches signature in dac_repository.py
    @abstractmethod
    async def get_latest_forecast(
        self, 
        building_id: str, 
        forecast_type: str, 
        horizon: str
    ) -> Optional[Forecast]: pass

class MockForecastRepository(IForecastRead):
    async def get_latest_forecast(
        self, 
        building_id: str, 
        forecast_type: str, 
        horizon: str
    ) -> Optional[Forecast]:
        
        now = datetime.utcnow()
        # DAC stores data in 'series_item' list of dicts
        series_data = []
        for i in range(24):
            series_data.append({
                "ts": now + timedelta(hours=i),
                "value": random.uniform(1000, 5000),
                "conf": 0.95
            })
            
        return Forecast(
            id="fc_repo_123",
            type=forecast_type,
            horizon=horizon,
            issued_at=now,
            requested_by="req_user_1",
            series_item=series_data, # Matches DAC field name
            valid_for={"from": now, "to": now + timedelta(hours=24)},
            model_meta={"algo": "XGBoost", "ver": "1.0"},
            scope={"buildingId": building_id}
        )