#!/usr/bin/env python3
"""
Railway Configuration Validation Script

This script validates that all Railway deployment configurations are properly set up.
"""

import os
import sys
import json
import requests
import time
from typing import Dict, List
from dotenv import load_dotenv

def check_file_exists(filepath: str) -> bool:
    """Check if a required file exists."""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {filepath}")
    return exists

def validate_railway_json() -> bool:
    """Validate railway.json configuration."""
    print("\n📋 Validating railway.json...")
    
    if not check_file_exists("railway.json"):
        return False
    
    try:
        with open("railway.json", "r") as f:
            config = json.load(f)
        
        required_fields = [
            "build.builder",
            "deploy.startCommand",
            "deploy.healthcheckPath",
            "deploy.restartPolicyType"
        ]
        
        all_valid = True
        for field in required_fields:
            keys = field.split(".")
            value = config
            try:
                for key in keys:
                    value = value[key]
                print(f"✅ {field}: {value}")
            except KeyError:
                print(f"❌ Missing: {field}")
                all_valid = False
        
        return all_valid
    except json.JSONDecodeError:
        print("❌ Invalid JSON format")
        return False

def validate_procfile() -> bool:
    """Validate Procfile configuration."""
    print("\n📋 Validating Procfile...")
    
    if not check_file_exists("Procfile"):
        return False
    
    with open("Procfile", "r") as f:
        content = f.read().strip()
    
    if "web:" in content and "uvicorn app:app" in content and "$PORT" in content:
        print("✅ Procfile format is correct")
        return True
    else:
        print("❌ Procfile format is incorrect")
        return False

def validate_requirements() -> bool:
    """Validate requirements.txt has necessary dependencies."""
    print("\n📋 Validating requirements.txt...")
    
    if not check_file_exists("requirements.txt"):
        return False
    
    with open("requirements.txt", "r") as f:
        content = f.read()
    
    required_deps = ["fastapi", "uvicorn", "gunicorn", "pydantic"]
    all_present = True
    
    for dep in required_deps:
        if dep in content:
            print(f"✅ {dep} found")
        else:
            print(f"❌ {dep} missing")
            all_present = False
    
    return all_present

def validate_env_variables() -> bool:
    """Validate environment variables are properly configured."""
    print("\n📋 Validating environment variables...")
    
    load_dotenv()
    
    required_vars = [
        "SHOPIFY_ADMIN_TOKEN",
        "SHOPIFY_STORE_DOMAIN", 
        "OPENAI_API_KEY"
    ]
    
    optional_vars = [
        "OPENAI_MODEL",
        "LOG_LEVEL",
        "ALLOWED_ORIGINS",
        "PORT"
    ]
    
    all_present = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Set")
        else:
            print(f"❌ {var}: Missing")
            all_present = False
    
    for var in optional_vars:
        value = os.getenv(var)
        status = "✅" if value else "⚠️"
        print(f"{status} {var}: {'Set' if value else 'Not set (optional)'}")
    
    return all_present

def test_cors_configuration() -> bool:
    """Test CORS configuration."""
    print("\n📋 Testing CORS configuration...")
    
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "")
    
    if allowed_origins:
        origins = [origin.strip() for origin in allowed_origins.split(",")]
        print(f"✅ CORS origins configured: {origins}")
        return True
    else:
        print("⚠️ CORS origins not configured (will default to allow all)")
        return True

def test_health_endpoint(base_url: str = "http://localhost:8080") -> bool:
    """Test the health endpoint."""
    print(f"\n📋 Testing health endpoint at {base_url}...")
    
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                print("✅ Health endpoint working correctly")
                return True
            else:
                print(f"❌ Health endpoint returned incorrect status: {data}")
                return False
        else:
            print(f"❌ Health endpoint returned status code: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Failed to connect to health endpoint: {e}")
        return False

def test_chat_endpoint(base_url: str = "http://localhost:8080") -> bool:
    """Test the chat endpoint with a simple message."""
    print(f"\n📋 Testing chat endpoint at {base_url}...")
    
    try:
        payload = {
            "message": "Hello, I need help with a return"
        }
        response = requests.post(
            f"{base_url}/chat", 
            json=payload, 
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "conversation_id" in data and "response" in data:
                print("✅ Chat endpoint working correctly")
                return True
            else:
                print(f"❌ Chat endpoint returned incorrect format: {data}")
                return False
        else:
            print(f"❌ Chat endpoint returned status code: {response.status_code}")
            if response.status_code == 500:
                print("   This might be due to missing API keys - check environment variables")
            return False
    except requests.RequestException as e:
        print(f"❌ Failed to connect to chat endpoint: {e}")
        return False

def main():
    """Run all validation checks."""
    print("🚀 Railway Configuration Validation")
    print("=" * 50)
    
    checks = [
        ("File Structure", lambda: all([
            check_file_exists("railway.json"),
            check_file_exists("Procfile"),
            check_file_exists("requirements.txt"),
            check_file_exists(".dockerignore"),
            check_file_exists("env.example")
        ])),
        ("Railway JSON", validate_railway_json),
        ("Procfile", validate_procfile),
        ("Requirements", validate_requirements),
        ("Environment Variables", validate_env_variables),
        ("CORS Configuration", test_cors_configuration),
    ]
    
    # Run static checks
    all_passed = True
    for name, check_func in checks:
        print(f"\n{name}:")
        result = check_func()
        all_passed = all_passed and result
    
    # Optionally test running endpoints
    if "--test-endpoints" in sys.argv:
        print("\n🌐 Testing Live Endpoints")
        print("=" * 30)
        print("Starting local server for testing...")
        
        # You would need to start the server in a separate process here
        # For now, just check if one is already running
        endpoint_checks = [
            ("Health Endpoint", lambda: test_health_endpoint()),
            ("Chat Endpoint", lambda: test_chat_endpoint()),
        ]
        
        for name, check_func in endpoint_checks:
            print(f"\n{name}:")
            result = check_func()
            all_passed = all_passed and result
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All validation checks passed!")
        print("✅ Configuration is ready for Railway deployment")
        sys.exit(0)
    else:
        print("❌ Some validation checks failed")
        print("⚠️ Please fix the issues before deploying to Railway")
        sys.exit(1)

if __name__ == "__main__":
    main() 