import motor.motor_asyncio
from beanie import init_beanie

from app.models.measurements import Measurement
from app.models.forecasts import Forecast
from app.models.core import UserAccount, Building, Floor, Room, Device

async def init_db(uri: str):
    client = motor.motor_asyncio.AsyncIOMotorClient(uri)
    db = client.Measurements
    
    await init_beanie(
        database=db, 
        document_models=[
            Measurement,
            Forecast,
            UserAccount, 
            Building,
            Floor,       
            Room,
            Device
        ]
    )