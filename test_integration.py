#!/usr/bin/env python3
"""
Integration test script to verify frontend-backend authentication flow
"""

import requests
import json
import time

# Backend URL
backend_url = "http://127.0.0.1:8000"

def test_backend_connection():
    """Test if backend is running"""
    try:
        response = requests.get(f"{backend_url}/health")
        if response.status_code == 200:
            print("✅ Backend is running and healthy")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server")
        return False

def test_user_registration():
    """Test user registration"""
    try:
        user_data = {
            "name": "Integration Test User",
            "email": "integration.test@example.com",
            "password": "TestPassword123!",
            "role": "User"
        }
        
        response = requests.post(f"{backend_url}/auth/register", json=user_data)
        
        if response.status_code == 200:
            print("✅ User registration successful")
            return response.json()
        elif response.status_code == 400:
            data = response.json()
            if "already registered" in data.get("detail", ""):
                print("⚠️  User already exists (this is expected if running test multiple times)")
                return {"email": user_data["email"]}
            else:
                print(f"❌ Registration failed: {data}")
                return None
        else:
            print(f"❌ Registration failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None

def test_user_login():
    """Test user login"""
    try:
        login_data = {
            "email": "integration.test@example.com",
            "password": "TestPassword123!"
        }
        
        response = requests.post(f"{backend_url}/auth/login-simple", json=login_data)
        
        if response.status_code == 200:
            print("✅ User login successful")
            return response.json()
        else:
            print(f"❌ Login failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_protected_endpoint(token):
    """Test accessing protected endpoint with token"""
    try:
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        response = requests.get(f"{backend_url}/auth/me", headers=headers)
        
        if response.status_code == 200:
            print("✅ Protected endpoint access successful")
            return response.json()
        else:
            print(f"❌ Protected endpoint failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Protected endpoint error: {e}")
        return None

def test_cors():
    """Test CORS configuration"""
    try:
        # Simulate a browser preflight request
        headers = {
            "Origin": "http://localhost:4200",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
        
        response = requests.options(f"{backend_url}/auth/login-simple", headers=headers)
        
        cors_header = response.headers.get("Access-Control-Allow-Origin")
        if cors_header and "localhost:4200" in cors_header:
            print("✅ CORS configuration is correct")
            return True
        else:
            print("⚠️  CORS might not be configured properly")
            return False
    except Exception as e:
        print(f"❌ CORS test error: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 Starting Integration Tests for Data2Paper Authentication System")
    print("=" * 60)
    
    # Test 1: Backend connectivity
    if not test_backend_connection():
        print("❌ Cannot proceed without backend connection")
        return
    
    # Test 2: User registration
    user = test_user_registration()
    if not user:
        print("❌ Cannot proceed without user registration")
        return
    
    # Test 3: User login
    auth_response = test_user_login()
    if not auth_response:
        print("❌ Cannot proceed without user login")
        return
    
    token = auth_response.get("access_token")
    if not token:
        print("❌ No access token received")
        return
    
    # Test 4: Protected endpoint
    user_info = test_protected_endpoint(token)
    if not user_info:
        print("❌ Protected endpoint test failed")
        return
    
    # Test 5: CORS
    test_cors()
    
    print("\n" + "=" * 60)
    print("🎉 Integration Tests Summary:")
    print("✅ Backend server is running")
    print("✅ User registration works")
    print("✅ User login works")
    print("✅ JWT authentication works")
    print("✅ Protected endpoints work")
    print("\n🚀 Your full-stack authentication system is ready!")
    print("\n📱 Frontend URL: http://localhost:4200")
    print("🔧 Backend API: http://127.0.0.1:8000")
    print("📚 API Docs: http://127.0.0.1:8000/docs")
    
    print(f"\n👤 Test User Created:")
    print(f"   Email: integration.test@example.com")
    print(f"   Password: TestPassword123!")

if __name__ == "__main__":
    main()
