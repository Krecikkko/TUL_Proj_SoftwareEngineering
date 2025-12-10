import asyncio
import os
from dotenv import load_dotenv
from app.database import init_db
from app.repositories.dac_repository import DataAccessGateway

async def main():
    """
    Main entry point for the Data Access and Control (DAC) Module.
    This script verifies configuration and database connectivity.
    """
    print("--- 🚀 Starting DAC Module ---")

    # 1. Load Environment Variables
    load_dotenv()
    uri = os.getenv("MONGO_URI")
    
    if not uri:
        print("❌ Error: MONGO_URI not found in .env file.")
        return

    # 2. Initialize Database Connection
    try:
        await init_db(uri)
        print("✅ Database Connection: ESTABLISHED")
    except Exception as e:
        print(f"❌ Database Connection: FAILED ({e})")
        return

    # 3. Initialize the Gateway (Your Core Component)
    try:
        dac = DataAccessGateway()
        print("✅ Data Access Gateway: INITIALIZED")
        print("   (Ready to serve IMeasurement, IForecastRead, IForecastWrite, ICoreDb)")
    except Exception as e:
        print(f"❌ Data Access Gateway: ERROR ({e})")
        return

    print("--- System Online and Waiting ---")

if __name__ == "__main__":
    # This ensures the code runs only when you execute 'python -m app.main'
    asyncio.run(main())