from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime, timedelta
import random
# Import 'Measurement' (new name) instead of 'MeasurementReading'
from DataModels4DAC import Measurement

class IMeasurement(ABC):
    @abstractmethod
    async def get_measurements(
        self,
        building_id: str,
        metric_type: str,
        start_date: datetime,
        end_date: datetime,
        device_ids: Optional[List[str]] = None
    ) -> List[Measurement]: pass

class MockMeasurementRepository(IMeasurement):
    async def get_measurements(
        self,
        building_id: str,
        metric_type: str,
        start_date: datetime,
        end_date: datetime,
        device_ids: Optional[List[str]] = None
    ) -> List[Measurement]:
        
        readings = []
        # Generate 5 data points for the requested range
        for i in range(5):
            ts = end_date - timedelta(hours=i)
            val = 0.0
            
            if metric_type == "power_w": val = random.uniform(4000, 6000)
            elif metric_type == "temp_c": val = random.uniform(20.0, 30.0)
            elif metric_type == "co2_ppm": val = random.uniform(400, 1200)
            elif metric_type == "humidity_pct": val = random.uniform(30, 60)

            readings.append(Measurement(
                id=f"m_{i}", 
                device_id="dev_mock_1", 
                metric=metric_type, 
                value=val, 
                timestamp=ts,
                tags={"room": "Room-101"}
            ))

        return readings