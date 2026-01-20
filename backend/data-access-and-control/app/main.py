import asyncio
import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
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
origins = [
    "http://localhost",
    "http://localhost:3000",  # React default port
    "http://localhost:5173",  # Vite default port
    "http://localhost:5174",  # Vite default port1
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://localhost:8000",  # FastAPI default port
    "http://localhost:8001",  # Alerts, Authentication and Communication Service
    "http://localhost:8002",  # Data Ingestion Service
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dac_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "ok", "component": "Data Access and Control"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8003, reload=True)

