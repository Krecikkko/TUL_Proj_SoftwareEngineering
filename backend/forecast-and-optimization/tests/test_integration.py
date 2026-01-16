"""
Integration Tests for Forecast & Optimization Module

These tests require the server to be running.
Start server first: uvicorn app.main:app --host 0.0.0.0 --port 8000

Then run: python tests/test_integration.py
"""

import requests
import time

API_BASE = "http://localhost:8000"


def test_health_check():
    """Test 1: Health Check"""
    print("\n" + "="*70)
    print("TEST 1: Health Check")
    print("="*70)
    
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["status"] == "healthy", "Status should be healthy"
        print("✅ PASSED: Health check working")
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def test_generate_forecast():
    """Test 2: Generate Forecast"""
    print("\n" + "="*70)
    print("TEST 2: Generate Energy Forecast")
    print("="*70)
    
    try:
        request_data = {
            "building_id": "TEST001",
            "horizon": "24H",
            "forecast_type": "energy_demand",
            "requested_by": "test_user"
        }
        
        response = requests.post(f"{API_BASE}/forecast", json=request_data, timeout=30)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "forecast_id" in data, "Response should have forecast_id"
        assert data["building_id"] == "TEST001", "Building ID should match"
        assert len(data["values"]) == 24, "Should have 24 hourly values"
        assert data["accuracy"] > 0, "Accuracy should be positive"
        
        print(f"✅ PASSED: Forecast generated (ID: {data['forecast_id']}, Accuracy: {data['accuracy']:.1%})")
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def test_generate_optimization():
    """Test 3: Generate Optimization"""
    print("\n" + "="*70)
    print("TEST 3: Generate Optimization Recommendations")
    print("="*70)
    
    try:
        request_data = {
            "building_id": "TEST002",
            "requested_by": "test_user",
            "time_range_hours": 24
        }
        
        response = requests.post(f"{API_BASE}/optimization", json=request_data, timeout=30)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "recommendations" in data, "Response should have recommendations"
        assert "total_potential_savings" in data, "Response should have total savings"
        assert data["building_id"] == "TEST002", "Building ID should match"
        
        print(f"✅ PASSED: Optimization generated ({len(data['recommendations'])} recommendations, {data['total_potential_savings']:.2f} zł/day savings)")
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def test_root_endpoint():
    """Test 4: Root Endpoint"""
    print("\n" + "="*70)
    print("TEST 4: Root Endpoint")
    print("="*70)
    
    try:
        response = requests.get(f"{API_BASE}/", timeout=5)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["service"] == "EMSIB Forecast & Optimization", "Service name should match"
        assert "team" in data, "Should have team info"
        
        print("✅ PASSED: Root endpoint working")
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def run_all_tests():
    """Run all integration tests"""
    print("\n" + "="*70)
    print("FORECAST & OPTIMIZATION - INTEGRATION TESTS")
    print("Team: Daniyar Zhumatayev & Kuzma Martysiuk")
    print("="*70)
    
    # Check if server is running
    print("\nChecking if server is running...")
    try:
        requests.get(f"{API_BASE}/", timeout=2)
        print("✅ Server is running\n")
    except:
        print("❌ ERROR: Server is not running!")
        print("Please start the server first:")
        print("  uvicorn app.main:app --host 0.0.0.0 --port 8000")
        print("\nThen run tests again: python tests/test_integration.py")
        return
    
    # Run tests
    results = []
    results.append(("Health Check", test_health_check()))
    results.append(("Generate Forecast", test_generate_forecast()))
    results.append(("Generate Optimization", test_generate_optimization()))
    results.append(("Root Endpoint", test_root_endpoint()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {name}")
    
    print("\n" + "="*70)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("="*70)
    
    if passed == total:
        print("\n🎉 All tests passed! Module is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check output above.")


if __name__ == "__main__":
    run_all_tests()
