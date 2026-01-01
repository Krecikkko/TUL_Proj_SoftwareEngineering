# main.py
from fastapi import FastAPI
import uvicorn

# Import the router from your AuthInterfaces.py file
# Note: You might need to remove the '.' from imports in AuthInterfaces.py
# if all files are in the same folder (e.g., 'from .IMeasurement' -> 'from IMeasurement')
from AuthInterfaces import router as gateway_router

app = FastAPI()

# Mount the router
app.include_router(gateway_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)