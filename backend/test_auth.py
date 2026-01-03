import requests
import json
import uuid

# Configuration
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

def test_auth_flow():
    print("Testing authentication flow...")
    
    # Generate unique email for this test run
    test_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    test_password = "SecurePassword123!"
    test_username = f"testuser_{uuid.uuid4().hex[:8]}"
    
    print(f"Using test email: {test_email}")
    
    # Step 1: Register a new user
    print("\n1. Testing registration...")
    register_data = {
        "email": test_email,
        "password": test_password,
        "username": test_username
    }
    
    try:
        response = requests.post(f"{BASE_URL}/rag/auth/register", 
                                headers=HEADERS, 
                                data=json.dumps(register_data))
        print(f"Registration response: {response.status_code}")
        print(f"Registration data: {response.json()}")
        
        if response.status_code != 200:
            print(f"Registration failed: {response.text}")
            return False
            
        register_result = response.json()
        user_id = register_result.get("user_id")
        
    except Exception as e:
        print(f"Registration error: {e}")
        return False
    
    # Step 2: Try to register with the same email (should fail)
    print("\n2. Testing duplicate registration (should fail)...")
    try:
        response = requests.post(f"{BASE_URL}/rag/auth/register", 
                                headers=HEADERS, 
                                data=json.dumps(register_data))
        print(f"Duplicate registration response: {response.status_code}")
        
        if response.status_code != 409:
            print(f"Expected 409 conflict for duplicate registration, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Duplicate registration test error: {e}")
        return False
    
    # Step 3: Login with the registered user
    print("\n3. Testing login...")
    login_data = {
        "email": test_email,
        "password": test_password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/rag/auth/login", 
                                headers=HEADERS, 
                                data=json.dumps(login_data))
        print(f"Login response: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Login failed: {response.text}")
            return False
            
        login_result = response.json()
        token = login_result.get("access_token")
        print(f"Login successful, token received: {'Yes' if token else 'No'}")
        
        if not token:
            print("No token received during login")
            return False
            
    except Exception as e:
        print(f"Login error: {e}")
        return False
    
    # Step 4: Try to login with wrong password (should fail)
    print("\n4. Testing login with wrong password (should fail)...")
    wrong_login_data = {
        "email": test_email,
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/rag/auth/login", 
                                headers=HEADERS, 
                                data=json.dumps(wrong_login_data))
        print(f"Wrong password login response: {response.status_code}")
        
        if response.status_code != 401:
            print(f"Expected 401 for wrong password, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Wrong password test error: {e}")
        return False
    
    print("\nAll authentication tests passed!")
    return True

if __name__ == "__main__":
    success = test_auth_flow()
    if success:
        print("\n✅ Authentication flow test completed successfully!")
    else:
        print("\n❌ Authentication flow test failed!")