from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime, timedelta
import random
from DataModels4DAC import MeasurementReading, DeviceMetadata

class IMeasurement(ABC):
    @abstractmethod
    async def get_building_metrics(self, building_id: str) -> List[MeasurementReading]: pass

class MockMeasurementRepository(IMeasurement):
    async def get_building_metrics(self, building_id: str) -> List[MeasurementReading]:
        # Returns aggregated data matching DAC schema
        return [
            MeasurementReading(
                deviceId="dev_A", 
                metric="power_w", 
                value=450.5, 
                ts=datetime.utcnow(),
                tags={"unit": "watt"}
            ),
            MeasurementReading(
                deviceId="dev_B", 
                metric="temp_c", 
                value=random.uniform(20.0, 32.0), # Random for testing alerts
                ts=datetime.utcnow(),
                tags={"unit": "celsius"}
            ),
            MeasurementReading(
                deviceId="dev_C", 
                metric="co2_ppm", 
                value=410, 
                ts=datetime.utcnow()
            )
        ]