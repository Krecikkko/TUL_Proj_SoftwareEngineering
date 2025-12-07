# FILE: backend/components/dac/interfaces/IMeasurement.py
from abc import ABC, abstractmethod
from typing import List
from datetime import datetime, timedelta
import random

# 1. IMPORT SHARED MODELS (Don't redefine them!)
from ...DataModels4DAC import MeasurementReading, DeviceStatus, MetricType

# --- THE INTERFACE ---
class IMeasurement(ABC):
    @abstractmethod
    async def get_current_reading(self, device_id: str) -> MeasurementReading:
        pass

    @abstractmethod
    async def get_historical_readings(self, device_id: str, start: datetime, end: datetime) -> List[MeasurementReading]:
        pass

    @abstractmethod
    async def get_building_metrics(self, building_id: str) -> List[MeasurementReading]:
        pass

    @abstractmethod
    async def get_device_status(self, device_id: str) -> DeviceStatus:
        pass

# --- THE MOCK IMPLEMENTATION ---
class MockMeasurementRepository(IMeasurement):
    """
    Simulates the Data Access Component (DAC) connecting to MetricsDb.
    """
    async def get_current_reading(self, device_id: str) -> MeasurementReading:
        return MeasurementReading(
            _id=f"read_{random.randint(1000, 9999)}",
            deviceId=device_id,
            metric=MetricType.POWER,
            value=round(random.uniform(50.0, 150.0), 2),
            ts=datetime.utcnow(),
            tags={"room": "Room-101", "floor": "1"}
        )

    async def get_historical_readings(self, device_id: str, start: datetime, end: datetime) -> List[MeasurementReading]:
        readings = []
        current_time = start
        while current_time <= end:
            readings.append(MeasurementReading(
                _id=f"hist_{random.randint(10000, 99999)}",
                deviceId=device_id,
                metric=MetricType.TEMPERATURE,
                value=round(random.uniform(18.0, 24.0), 1),
                ts=current_time,
                tags={"room": "Room-101"}
            ))
            current_time += timedelta(minutes=15)
        return readings

    async def get_building_metrics(self, building_id: str) -> List[MeasurementReading]:
        # Returns aggregated data for the Dashboard
        return [
            MeasurementReading(_id="agg_1", deviceId="dev_A", metric=MetricType.POWER, value=450.5, ts=datetime.utcnow()),
            MeasurementReading(_id="agg_2", deviceId="dev_B", metric=MetricType.TEMPERATURE, value=22.1, ts=datetime.utcnow()),
            MeasurementReading(_id="agg_3", deviceId="dev_C", metric=MetricType.CO2, value=410, ts=datetime.utcnow())
        ]

    async def get_device_status(self, device_id: str) -> DeviceStatus:
        return DeviceStatus(
            _id=device_id,
            last={"temp_set": 21.5, "on": True, "power_w": 120},
            updatedAt=datetime.utcnow()
        )