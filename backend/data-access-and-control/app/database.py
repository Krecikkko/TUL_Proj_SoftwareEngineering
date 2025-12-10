import motor.motor_asyncio
from beanie import init_beanie

# Only import the models that ACTUALLY exist in the MongoDB
from app.models.measurements import Measurement
from app.models.forecasts import Forecast
# We DO NOT import User/Building/Room here because we don't want to create them

async def init_db(uri: str):
    client = motor.motor_asyncio.AsyncIOMotorClient(uri)
    
    #
    db = client.Measurements
    
    # Only register models for collections that exist or that you own
    await init_beanie(
        database=db, 
        document_models=[
            Measurement,
            Forecast
        ]
    )