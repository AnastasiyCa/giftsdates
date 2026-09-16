#!/usr/bin/env python3
"""
Quick test for GET /api/profiles?intent=marriage filter
"""
import requests
from datetime import datetime

BASE_URL = "https://login-vault-30.preview.emergentagent.com/api"

# Register and login a test user
timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
email = f"filter.test.{timestamp}@test.com"
password = "SecurePass123!"

payload = {
    "email": email,
    "password": password,
    "name": "Filter Test User",
    "age": 28,
    "gender": "female",
    "interested_in": "male",
    "city": "New York",
    "country": "USA"
}

print("Registering test user...")
response = requests.post(f"{BASE_URL}/auth/register", json=payload, timeout=10)
if response.status_code != 200:
    print(f"Registration failed: {response.status_code}")
    exit(1)

token = response.json().get("token")
print(f"✓ Registered and got token")

# Try GET /api/profiles?intent=marriage
headers = {"Authorization": f"Bearer {token}"}

print("\nTesting GET /api/profiles?intent=marriage...")
response = requests.get(f"{BASE_URL}/profiles?intent=marriage", headers=headers, timeout=10)

print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")

if response.status_code == 403:
    data = response.json()
    if "PREMIUM_REQUIRED" in response.text:
        print("\n✓ Expected behavior: PREMIUM_REQUIRED for advanced filters")
        print("This is correct - the intent filter requires Premium status")
    else:
        print(f"\n✗ Unexpected 403 error: {data}")
elif response.status_code == 200:
    profiles = response.json()
    print(f"\n✓ Filter worked! Returned {len(profiles)} profiles")
    # Check if any have relationship_intent containing "marriage"
    with_marriage = [p for p in profiles if isinstance(p.get('relationship_intent'), list) and 'marriage' in p.get('relationship_intent', [])]
    print(f"Profiles with 'marriage' in relationship_intent: {len(with_marriage)}")
else:
    print(f"\n✗ Unexpected status code: {response.status_code}")
