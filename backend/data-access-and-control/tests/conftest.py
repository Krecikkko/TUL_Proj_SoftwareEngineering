import pytest
import asyncio
from beanie import init_beanie
from mongomock_motor import AsyncMongoMockClient
from app.models.measurements import Measurement
from app.models.forecasts import Forecast

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db_client():

    client = AsyncMongoMockClient()
    test_db = client.Test_Measurements_DB
    
    await init_beanie(
        database=test_db,
        document_models=[Measurement, Forecast]
    )
    
    yield test_db