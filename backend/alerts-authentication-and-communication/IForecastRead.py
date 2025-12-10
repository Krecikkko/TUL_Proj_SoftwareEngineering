from abc import ABC, abstractmethod
from typing import List
from datetime import datetime, timedelta
import random
from DataModels4DAC import Forecast, ForecastSeriesItem

class IForecastRead(ABC):
    """
    Interface provided by DAC for reading predictions from MongoDB.
    """
    @abstractmethod
    async def get_latest_demand_forecast(self, building_id: str) -> Forecast:
        pass

# --- MOCK FOR AAC TESTING ---
class MockForecastRepository(IForecastRead):
    async def get_latest_demand_forecast(self, building_id: str) -> Forecast:
        # Generate 24h of fake demand data
        start = datetime.utcnow()
        series = []
        for i in range(24):
            series.append(ForecastSeriesItem(
                ts=start + timedelta(hours=i),
                value=random.uniform(1000, 5000) # Fake kW demand
            ))
            
        return Forecast(
            _id="fc_newest",
            type="energy_demand",
            horizon="PT24H",
            issued_at=start,
            series=series
        )