import asyncio
from datetime import datetime, timedelta
from AuthInterfaces import get_aac_service, UserLogin

async def run_test_scenario():
    print("--- STARTING SYSTEM TEST (FRONTEND + BACKEND ALIGNMENT) ---")

    service = await get_aac_service()
    print("[V] Service initialized")


    print("\n--- TEST 1: LOGIN ---")
    try:
        login_data = UserLogin(username="admin", password="secret")
        auth_token = await service.login_user(login_data)
        token = auth_token.access_token
        print(f"[V] Login OK. Token: {token[:10]}...")
    except Exception as e:
        print(f"[X] Login Failed: {e}")
        return

    print("\n--- TEST 2: ALERTS (Frontend Format) ---")
    try:
        alerts = await service.get_system_alerts(token)
        if alerts:
            for a in alerts:
                print(f"    [!] {a.severity.value}: {a.message} (Bldg: {a.building_id})")
        else:
            print("    [i] No alerts (Normal operation)")
    except Exception as e:
        print(f"[X] Alerts Failed: {e}")

    print("\n--- TEST 3: MEASUREMENTS (Data Viz) ---")
    try:
        data = await service.get_measurements_view(
            buildingId="B1",
            metric="temperature", 
            fromDate=datetime.utcnow() - timedelta(hours=5),
            toDate=datetime.utcnow()
        )
        print(f"[V] Received {len(data)} points")
        if data:
            print(f"    Sample: {data[0].metric} = {data[0].value} at {data[0].ts}")
            if hasattr(data[0], 'ts') and data[0].metric == "temperature":
                print("[V] Translation (timestamp->ts, temp_c->temperature) Successful")
    except Exception as e:
        print(f"[X] Measurements Failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_test_scenario())