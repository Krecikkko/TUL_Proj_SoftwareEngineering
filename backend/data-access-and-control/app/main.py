import asyncio
import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv

from app.database import init_db
from app.api.routes import router as dac_router
#from app.repositories.dac_repository import DataAccessGateway

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    uri = os.getenv("MONGO_URI")

    if not uri:
        print("Error: MONGO_URI not found in .env file")
    else:
        try:
            await init_db(uri)
            print("Database connection: ESTABLISHED")
        except Exception as e:
            print(f"Database connection: FAILED ({e})")

    yield 

app = FastAPI(
    title = "Data Access and Control API", 
    description = "API for accessing Measurements, Forecasts and Core Data", 
    version = "1.0.0", 
    lifespan = lifespan
)

app.include_router(dac_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "ok", "component": "Data Access and Control"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

