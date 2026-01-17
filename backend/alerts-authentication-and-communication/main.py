# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import the router from your AuthInterfaces.py file
# Note: You might need to remove the '.' from imports in AuthInterfaces.py
# if all files are in the same folder (e.g., 'from .IMeasurement' -> 'from IMeasurement')
from AuthInterfaces import router as gateway_router

app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:3000",  # React default port
    "http://localhost:5173",  # Vite default port
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the router
app.include_router(gateway_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)