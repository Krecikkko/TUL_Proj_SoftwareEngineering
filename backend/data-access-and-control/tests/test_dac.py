import pytest
from datetime import datetime, timedelta
from app.repositories.dac_repository import DataAccessGateway
from app.models.measurements import Measurement

@pytest.mark.asyncio
async def test_create_and_read_measurement(db_client):
    dac = DataAccessGateway()
    now = datetime.utcnow()
    
    measurement = Measurement(
        deviceId="sensor_01",
        metric="temperature",
        value=22.5,
        ts=now,
        tags={"unit": "C"}
    )
    await measurement.insert()

    results = await dac.get_measurements(
        building_id="b_01", 
        metric_type="temperature",
        start_date=now - timedelta(minutes=10),
        end_date=now + timedelta(minutes=10),
        device_ids=["sensor_01"]
    )

    assert len(results) == 1
    assert results[0].value == 22.5
    assert results[0].device_id == "sensor_01"

@pytest.mark.asyncio
async def test_create_forecast(db_client):

    dac = DataAccessGateway()
    valid_from = datetime.utcnow()
    valid_to = valid_from + timedelta(hours=1)
    series_data = [{"ts": valid_from, "value": 100}]


    forecast_id = await dac.create_forecast(
        forecast_type="energy_demand",
        horizon="1H",
        building_id="building_123",
        requested_by="user_test",
        series_data=series_data,
        valid_from=valid_from,
        valid_to=valid_to,
        model_algorithm="XGBoost",
        model_version="1.0"
    )


    assert forecast_id is not None
    fetched_forecast = await dac.get_forecast_by_id(forecast_id)
    assert fetched_forecast is not None
    assert fetched_forecast.type == "energy_demand"
    assert fetched_forecast.scope["buildingId"] == "building_123"