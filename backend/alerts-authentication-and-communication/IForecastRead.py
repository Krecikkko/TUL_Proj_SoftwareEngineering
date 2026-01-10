from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import random
from DataModels4DAC import Forecast

class IForecastRead(ABC):
    @abstractmethod
    async def get_latest_demand_forecast(self, building_id: str) -> Forecast: pass

class MockForecastRepository(IForecastRead):
    async def get_latest_demand_forecast(self, building_id: str) -> Forecast:
        now = datetime.utcnow()
        # Generate series as a list of dictionaries (not Objects!)
        series_data = []
        for i in range(24):
            series_data.append({
                "ts": now + timedelta(hours=i),
                "value": random.uniform(1000, 5000),
                "conf": 0.95
            })
            
        return Forecast(
            _id="fc_newest",
            type="energy_demand",
            horizon="1D",
            issued_at=now,
            requested_by="req_uuid_123",
            series_item=series_data, # Updated field name
            valid_for={"from": now, "to": now + timedelta(hours=24)},
            model_meta={"algo": "LSTM", "ver": "v1.2"}
        )