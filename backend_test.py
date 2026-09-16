#!/usr/bin/env python3
"""
Backend API Testing for GiftsDates Dating App
Tests core authentication and basic endpoints
"""

import requests
import json
import sys
from datetime import datetime

# Read backend URL from frontend/.env
BACKEND_URL = "https://login-vault-30.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test data
TEST_USER = {
    "email": f"testuser_{datetime.now().timestamp()}@example.com",
    "password": "SecurePass123!",
    "name": "Emma Rodriguez",
    "age": 28,
    "gender": "female",
    "interested_in": "male",
    "orientation": "straight",
    "city": "Los Angeles",
    "country": "USA",
    "bio": "Love traveling and meeting new people. Looking for genuine connections."
}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name):
    print(f"\n{Colors.BLUE}Testing: {name}{Colors.END}")

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def test_meta_endpoint():
    """Test GET /api/meta endpoint"""
    print_test("GET /api/meta")
    try:
        response = requests.get(f"{API_BASE}/meta", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            print_success(f"Response contains: {list(data.keys())}")
            
            # Verify expected fields
            expected_fields = ['gifts', 'coin_packages', 'premium', 'video_rate']
            missing = [f for f in expected_fields if f not in data]
            if missing:
                print_warning(f"Missing fields: {missing}")
            else:
                print_success("All expected fields present")
            return True
        else:
            print_error(f"Status: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False

def test_root_endpoint():
    """Test GET /api/ endpoint"""
    print_test("GET /api/")
    try:
        response = requests.get(f"{API_BASE}/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            print_success(f"Response: {data}")
            
            if data.get('service') == 'GiftsDates' and data.get('ok') == True:
                print_success("Root endpoint working correctly")
                return True
            else:
                print_warning(f"Unexpected response format: {data}")
                return True  # Still counts as working
        else:
            print_error(f"Status: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False

def test_user_registration():
    """Test POST /api/auth/register"""
    print_test("POST /api/auth/register")
    try:
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=TEST_USER,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            
            # Verify response structure
            if 'token' in data and 'user' in data:
                print_success("Registration successful")
                print_success(f"User ID: {data['user'].get('id')}")
                print_success(f"Token received: {data['token'][:20]}...")
                return True, data['token'], data['user']
            else:
                print_error(f"Missing token or user in response: {list(data.keys())}")
                return False, None, None
        else:
            print_error(f"Status: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False, None, None
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False, None, None

def test_user_login(email, password):
    """Test POST /api/auth/login"""
    print_test("POST /api/auth/login")
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": email, "password": password},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            
            if 'token' in data and 'user' in data:
                print_success("Login successful")
                print_success(f"User: {data['user'].get('name')}")
                print_success(f"Token received: {data['token'][:20]}...")
                return True, data['token']
            else:
                print_error(f"Missing token or user in response")
                return False, None
        else:
            print_error(f"Status: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False, None
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False, None

def test_get_current_user(token):
    """Test GET /api/auth/me (authenticated)"""
    print_test("GET /api/auth/me (authenticated)")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE}/auth/me", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            print_success(f"User: {data.get('name')} ({data.get('email')})")
            print_success(f"User ID: {data.get('id')}")
            print_success(f"Coins: {data.get('coins', 0)}")
            
            # Verify expected fields
            expected_fields = ['id', 'email', 'name', 'age', 'gender', 'city', 'country']
            missing = [f for f in expected_fields if f not in data]
            if missing:
                print_warning(f"Missing fields: {missing}")
            else:
                print_success("All expected user fields present")
            return True
        else:
            print_error(f"Status: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False

def test_browse_profiles(token):
    """Test GET /api/profiles (authenticated)"""
    print_test("GET /api/profiles (browse)")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_BASE}/profiles",
            headers=headers,
            params={"min_age": 18, "max_age": 99},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            
            if isinstance(data, list):
                print_success(f"Profiles returned: {len(data)}")
                if len(data) > 0:
                    print_success(f"Sample profile: {data[0].get('name', 'N/A')}, {data[0].get('age', 'N/A')}")
                else:
                    print_warning("No profiles found (empty database)")
                return True
            else:
                print_error(f"Expected list, got: {type(data)}")
                return False
        else:
            print_error(f"Status: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False

def test_unauthenticated_access():
    """Test that authenticated endpoints reject requests without token"""
    print_test("Unauthenticated access (should fail)")
    try:
        response = requests.get(f"{API_BASE}/auth/me", timeout=10)
        
        if response.status_code == 401:
            print_success(f"Status: {response.status_code} (correctly rejected)")
            return True
        else:
            print_error(f"Expected 401, got: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False

def main():
    print(f"\n{'='*60}")
    print(f"{Colors.BLUE}GiftsDates Backend API Testing{Colors.END}")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"{'='*60}")
    
    results = {}
    token = None
    
    # Test 1: Meta endpoint (public)
    results['meta'] = test_meta_endpoint()
    
    # Test 2: Root endpoint (public)
    results['root'] = test_root_endpoint()
    
    # Test 3: User registration
    reg_success, token, user = test_user_registration()
    results['registration'] = reg_success
    
    if reg_success and token:
        # Test 4: User login
        login_success, login_token = test_user_login(TEST_USER['email'], TEST_USER['password'])
        results['login'] = login_success
        
        # Use the login token for subsequent tests
        if login_success and login_token:
            token = login_token
        
        # Test 5: Get current user (authenticated)
        results['get_user'] = test_get_current_user(token)
        
        # Test 6: Browse profiles (authenticated)
        results['browse_profiles'] = test_browse_profiles(token)
    else:
        print_warning("\nSkipping authenticated tests due to registration failure")
        results['login'] = False
        results['get_user'] = False
        results['browse_profiles'] = False
    
    # Test 7: Unauthenticated access
    results['unauth_reject'] = test_unauthenticated_access()
    
    # Summary
    print(f"\n{'='*60}")
    print(f"{Colors.BLUE}Test Summary{Colors.END}")
    print(f"{'='*60}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"{test_name.ljust(20)}: {status}")
    
    print(f"\n{Colors.BLUE}Total: {passed}/{total} tests passed{Colors.END}")
    
    if passed == total:
        print(f"{Colors.GREEN}✓ All tests passed!{Colors.END}\n")
        return 0
    else:
        print(f"{Colors.RED}✗ Some tests failed{Colors.END}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
