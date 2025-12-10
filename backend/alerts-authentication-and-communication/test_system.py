import asyncio
from AuthInterfaces import get_aac_service, UserLogin

async def run_test_scenario():
    print("--- STARTING SYSTEM TEST ---")

    # 1. INITIALIZE THE SERVICE
    # This manually injects the mocks just like the API would
    service = await get_aac_service()
    print("[✓] Service initialized with Mocks")

    # 2. TEST AUTHENTICATION
    print("\n--- TEST 1: LOGIN ---")
    try:
        login_data = UserLogin(username="admin", password="secret")
        auth_token = await service.login_user(login_data)
        print(f"[✓] Login Successful!")
        print(f"    Token: {auth_token.access_token}")
        print(f"    Role:  {auth_token.role}")
        
        # Save token for next steps
        token = auth_token.access_token
    except Exception as e:
        print(f"[X] Login Failed: {e}")
        return

    # 3. TEST DASHBOARD (Communication)
    print("\n--- TEST 2: DASHBOARD FETCH ---")
    try:
        dashboard = await service.get_dashboard_view(token)
        print(f"[✓] Dashboard Data Retrieved:")
        print(f"    Power Usage:   {dashboard.current_power_usage} W")
        print(f"    Avg Temp:      {dashboard.temperature_avg} C")
        print(f"    Active Alerts: {dashboard.active_alerts_count}")
        print(f"    Forecast:      {dashboard.forecast_summary}")
    except Exception as e:
        print(f"[X] Dashboard Fetch Failed: {e}")

    # 4. TEST ALERTS (Alerts)
    print("\n--- TEST 3: ALERT DETECTION ---")
    try:
        alerts = await service.get_system_alerts(token)
        print(f"[✓] Alerts Check Complete")
        if alerts:
            print(f"    [!] ALERT DETECTED: {len(alerts)} active")
            for a in alerts:
                print(f"        - [{a.severity}] {a.message} (Device: {a.device_id})")
        else:
            print("    [i] System Nominal (No alerts triggered by random mock data)")
    except Exception as e:
        print(f"[X] Alert Check Failed: {e}")

if __name__ == "__main__":
    # Run the async test function
    asyncio.run(run_test_scenario())