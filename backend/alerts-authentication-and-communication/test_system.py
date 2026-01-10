import sys
import asyncio

print("--- SYSTEM BOOT INIT ---") 

try:
    print("[*] Loading modules...")
    # Import logic and models
    from AuthInterfaces import get_aac_service, UserLogin
    # Import the new UserRole enum to verify login roles
    from DataModels4DAC import UserRole 
    print("[*] Modules loaded successfully.")

except ImportError as e:
    print(f"\n[!!!] CRITICAL IMPORT ERROR: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n[!!!] UNEXPECTED ERROR: {e}")
    sys.exit(1)

async def run_test_scenario():
    print("\n--- STARTING TEST SCENARIO (DAC ALIGNMENT) ---")

    # 1. INITIALIZE SERVICE
    try:
        service = await get_aac_service()
        print("[✓] AAC Gateway Service Started with DAC-aligned Mocks")
    except Exception as e:
        print(f"[X] Service Init Failed: {e}")
        return

    # 2. TEST AUTHENTICATION
    print("\n--- TEST 1: AUTHENTICATION ---")
    token = None
    try:
        # We test with the admin user defined in MockCoreDb
        login_data = UserLogin(username="admin", password="secret")
        auth_token = await service.login_user(login_data)
        
        print(f"[✓] Login Successful")
        print(f"    Token: {auth_token.access_token}")
        print(f"    Role:  {auth_token.role}")
        
        if auth_token.role == UserRole.ADMIN.value:
             print("    [✓] Role Verification Passed")
        
        token = auth_token.access_token
    except Exception as e:
        print(f"[X] Login Failed: {e}")
        return

    # 3. TEST DASHBOARD
    print("\n--- TEST 2: DASHBOARD (DAC DATA AGGREGATION) ---")
    try:
        dash = await service.get_dashboard_view(token)
        print(f"[✓] Dashboard Data Received:")
        print(f"    - Power Usage:   {dash.current_power_usage} W")
        print(f"    - Avg Temp:      {dash.temperature_avg} C")
        print(f"    - Active Alerts: {dash.active_alerts_count}")
        print(f"    - Forecast:      {dash.forecast_summary}")
        
        # Validation
        if "expected to reach" in dash.forecast_summary:
            print("    [✓] Forecast Summary logic valid")
    except Exception as e:
        print(f"[X] Dashboard Failed: {e}")

    # 4. TEST ALERTS
    print("\n--- TEST 3: ALERT LOGIC (NEW SCHEMA) ---")
    try:
        alerts = await service.get_system_alerts(token)
        if len(alerts) > 0:
            print(f"[✓] Alerts Triggered: {len(alerts)}")
            for a in alerts:
                # Note: We check 'device_id' which maps to DAC 'deviceId'
                print(f"    [!] {a.severity.value.upper()}: {a.message} (Device: {a.device_id})")
        else:
            print("[i] No alerts triggered (Random values within safe range).")
            print("    (Run again or tweak IMeasurement.py to force alerts)")
            
    except Exception as e:
        print(f"[X] Alerts Failed: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(run_test_scenario())
        print("\n--- TEST COMPLETE ---")
    except KeyboardInterrupt:
        print("\n[!] Test Interrupted")