#!/usr/bin/env python3
"""
Backend API tests for GiftsDates - Testing new registration fields and zodiac feature
"""
import requests
import json
from datetime import datetime

# Backend URL from frontend/.env
BASE_URL = "https://login-vault-30.preview.emergentagent.com/api"

def print_test(name, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {name}")
    if details:
        print(f"  Details: {details}")
    print()

def test_register_with_new_fields():
    """Test 1: POST /api/auth/register with new fields (language, birth_day, birth_month, birth_year)"""
    print("=" * 80)
    print("TEST 1: Register with new fields and zodiac computation")
    print("=" * 80)
    
    # Generate unique email for this test
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    email = f"sophia.martinez.{timestamp}@test.com"
    
    payload = {
        "email": email,
        "password": "SecurePass123!",
        "name": "Sophia Martinez",
        "age": 25,  # This should be overridden by computed age
        "gender": "female",
        "interested_in": "male",
        "orientation": "straight",
        "city": "Barcelona",
        "country": "Spain",
        "bio": "Love traveling and meeting new people",
        "language": "es",
        "birth_year": 1995,
        "birth_month": 8,
        "birth_day": 15
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=payload, timeout=10)
        
        if response.status_code != 200:
            print_test("Register with new fields", False, f"Status: {response.status_code}, Response: {response.text}")
            return None, None
        
        data = response.json()
        token = data.get("token")
        user = data.get("user")
        
        # Verify all fields
        checks = []
        checks.append(("Token returned", token is not None))
        checks.append(("User object returned", user is not None))
        checks.append(("Language is 'es'", user.get("language") == "es"))
        checks.append(("Birth date is '1995-08-15'", user.get("birth_date") == "1995-08-15"))
        checks.append(("Zodiac is 'leo'", user.get("zodiac") == "leo"))
        
        # Age should be computed (~30 in 2026, not the passed 25)
        computed_age = user.get("age")
        age_correct = computed_age is not None and 29 <= computed_age <= 31
        checks.append((f"Age auto-computed (~30, got {computed_age})", age_correct))
        
        all_passed = all(check[1] for check in checks)
        
        details = "\n    ".join([f"{check[0]}: {'✓' if check[1] else '✗'}" for check in checks])
        print_test("Register with new fields", all_passed, details)
        
        if all_passed:
            print(f"  User ID: {user.get('id')}")
            print(f"  Token: {token[:20]}...")
            return token, user
        else:
            return None, None
            
    except Exception as e:
        print_test("Register with new fields", False, f"Exception: {str(e)}")
        return None, None

def test_expanded_orientation():
    """Test 2: Register with expanded orientation values (pansexual, demisexual)"""
    print("=" * 80)
    print("TEST 2: Register with expanded orientation values")
    print("=" * 80)
    
    orientations_to_test = ["pansexual", "demisexual"]
    results = []
    
    for orientation in orientations_to_test:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        email = f"alex.{orientation}.{timestamp}@test.com"
        
        payload = {
            "email": email,
            "password": "SecurePass123!",
            "name": f"Alex {orientation.capitalize()}",
            "age": 28,
            "gender": "non-binary",
            "interested_in": "all",
            "orientation": orientation,
            "city": "San Francisco",
            "country": "USA",
            "language": "en"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/register", json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                user = data.get("user")
                stored_orientation = user.get("orientation")
                
                passed = stored_orientation == orientation
                results.append((orientation, passed, stored_orientation))
                print(f"  {orientation}: {'✓' if passed else '✗'} (stored as: {stored_orientation})")
            else:
                results.append((orientation, False, f"HTTP {response.status_code}"))
                print(f"  {orientation}: ✗ (HTTP {response.status_code})")
                
        except Exception as e:
            results.append((orientation, False, str(e)))
            print(f"  {orientation}: ✗ (Exception: {str(e)})")
    
    all_passed = all(r[1] for r in results)
    print_test("Expanded orientation values", all_passed)
    
    return all_passed

def test_login_and_me(token, expected_user):
    """Test 3: Login and GET /api/auth/me to verify persistence"""
    print("=" * 80)
    print("TEST 3: Login and GET /api/auth/me - verify zodiac, birth_date, language persist")
    print("=" * 80)
    
    # First, login with the user credentials
    login_payload = {
        "email": expected_user.get("email"),
        "password": "SecurePass123!"
    }
    
    try:
        # Test login
        login_response = requests.post(f"{BASE_URL}/auth/login", json=login_payload, timeout=10)
        
        if login_response.status_code != 200:
            print_test("Login", False, f"Status: {login_response.status_code}")
            return False
        
        login_data = login_response.json()
        new_token = login_data.get("token")
        print(f"  Login successful, token: {new_token[:20]}...")
        
        # Test GET /api/auth/me
        headers = {"Authorization": f"Bearer {new_token}"}
        me_response = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=10)
        
        if me_response.status_code != 200:
            print_test("GET /api/auth/me", False, f"Status: {me_response.status_code}")
            return False
        
        user = me_response.json()
        
        # Verify persistence
        checks = []
        checks.append(("Zodiac persisted", user.get("zodiac") == "leo"))
        checks.append(("Birth date persisted", user.get("birth_date") == "1995-08-15"))
        checks.append(("Language persisted", user.get("language") == "es"))
        
        all_passed = all(check[1] for check in checks)
        details = "\n    ".join([f"{check[0]}: {'✓' if check[1] else '✗'}" for check in checks])
        
        print_test("Login and GET /api/auth/me", all_passed, details)
        return all_passed
        
    except Exception as e:
        print_test("Login and GET /api/auth/me", False, f"Exception: {str(e)}")
        return False

def test_update_birth_date(token):
    """Test 4: PATCH /api/auth/me to update birth date and verify zodiac recomputation"""
    print("=" * 80)
    print("TEST 4: PATCH /api/auth/me - update birth date and verify zodiac recomputation")
    print("=" * 80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Update birth date to December 25, 1990 (should be Capricorn)
    update_payload = {
        "birth_year": 1990,
        "birth_month": 12,
        "birth_day": 25
    }
    
    try:
        response = requests.patch(f"{BASE_URL}/auth/me", json=update_payload, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print_test("PATCH /api/auth/me", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
        
        user = response.json()
        
        # Verify updates
        checks = []
        checks.append(("Birth date updated to '1990-12-25'", user.get("birth_date") == "1990-12-25"))
        checks.append(("Zodiac recomputed to 'capricorn'", user.get("zodiac") == "capricorn"))
        
        # Age should be recomputed (~35-36 in 2026)
        computed_age = user.get("age")
        age_correct = computed_age is not None and 34 <= computed_age <= 36
        checks.append((f"Age recomputed (~35, got {computed_age})", age_correct))
        
        all_passed = all(check[1] for check in checks)
        details = "\n    ".join([f"{check[0]}: {'✓' if check[1] else '✗'}" for check in checks])
        
        print_test("PATCH /api/auth/me - birth date update", all_passed, details)
        return all_passed
        
    except Exception as e:
        print_test("PATCH /api/auth/me", False, f"Exception: {str(e)}")
        return False

def test_profiles_zodiac_field(token):
    """Test 5: GET /api/profiles to verify zodiac field is included"""
    print("=" * 80)
    print("TEST 5: GET /api/profiles - verify zodiac field is included")
    print("=" * 80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/profiles", headers=headers, timeout=10)
        
        if response.status_code != 200:
            print_test("GET /api/profiles", False, f"Status: {response.status_code}")
            return False
        
        profiles = response.json()
        
        if not isinstance(profiles, list):
            print_test("GET /api/profiles", False, "Response is not a list")
            return False
        
        # Check if any profiles have zodiac field
        profiles_with_zodiac = [p for p in profiles if "zodiac" in p and p.get("zodiac") is not None]
        
        # The test passes if:
        # 1. The endpoint returns successfully (200)
        # 2. The zodiac field is present in profiles that have it set
        # Note: Older profiles may not have zodiac field, which is expected
        
        checks = []
        checks.append(("Profiles endpoint returns 200", True))
        checks.append(("Response is a list", True))
        
        # Check if zodiac field exists in the response structure (even if null for some profiles)
        has_zodiac_field = any("zodiac" in p for p in profiles)
        checks.append(("Zodiac field exists in profile structure", has_zodiac_field or len(profiles) == 0))
        
        all_passed = all(check[1] for check in checks)
        
        details = f"Total profiles: {len(profiles)}, Profiles with zodiac field: {sum(1 for p in profiles if 'zodiac' in p)}, Profiles with zodiac value: {len(profiles_with_zodiac)}"
        if profiles_with_zodiac:
            sample = profiles_with_zodiac[0]
            details += f"\n    Sample: {sample.get('name')} - zodiac: {sample.get('zodiac')}"
        elif profiles:
            # Show a sample profile to see what fields are present
            sample = profiles[0]
            details += f"\n    Sample profile fields: {list(sample.keys())}"
        
        print_test("GET /api/profiles - zodiac field", all_passed, details)
        return all_passed
        
    except Exception as e:
        print_test("GET /api/profiles", False, f"Exception: {str(e)}")
        return False

def main():
    print("\n" + "=" * 80)
    print("GIFTSDATES BACKEND API TESTS - NEW REGISTRATION FIELDS & ZODIAC FEATURE")
    print("=" * 80)
    print(f"Backend URL: {BASE_URL}")
    print(f"Test started at: {datetime.now().isoformat()}")
    print("=" * 80 + "\n")
    
    results = {}
    
    # Test 1: Register with new fields
    token, user = test_register_with_new_fields()
    results["Test 1: Register with new fields"] = token is not None
    
    # Test 2: Expanded orientation values
    results["Test 2: Expanded orientation"] = test_expanded_orientation()
    
    # Only continue with tests 3-5 if we have a valid token from test 1
    if token and user:
        # Test 3: Login and GET /api/auth/me
        results["Test 3: Login and GET /api/auth/me"] = test_login_and_me(token, user)
        
        # Test 4: PATCH /api/auth/me
        results["Test 4: PATCH /api/auth/me"] = test_update_birth_date(token)
        
        # Test 5: GET /api/profiles
        results["Test 5: GET /api/profiles"] = test_profiles_zodiac_field(token)
    else:
        print("⚠️  Skipping tests 3-5 due to test 1 failure\n")
        results["Test 3: Login and GET /api/auth/me"] = False
        results["Test 4: PATCH /api/auth/me"] = False
        results["Test 5: GET /api/profiles"] = False
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    total_tests = len(results)
    passed_tests = sum(1 for p in results.values() if p)
    
    print("=" * 80)
    print(f"TOTAL: {passed_tests}/{total_tests} tests passed")
    print("=" * 80 + "\n")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
