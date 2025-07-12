"""
Integration Test Configuration and Fixtures

This file provides test fixtures and configuration for integration and performance testing.
"""

import pytest
import requests
import os
import uuid
import time
from dotenv import load_dotenv
from typing import Dict, Any, Optional
import json

# Load environment variables
load_dotenv()

@pytest.fixture(scope="session")
def api_base_url():
    """Return the base URL for the deployed application"""
    # Try to detect the correct API URL
    api_url = os.environ.get("API_BASE_URL") 
    if not api_url:
        # Try common Railway patterns
        api_url = os.environ.get("RAILWAY_STATIC_URL")
        if api_url:
            api_url = f"https://{api_url}"
        else:
            # Fallback to default
            api_url = "https://returnbot-production.up.railway.app"
    
    return api_url

@pytest.fixture(scope="session")
def test_headers():
    """Return headers for API requests"""
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Integration-Test-Suite/1.0"
    }

@pytest.fixture(scope="session")
def test_order_data():
    """Return test order data for integration tests"""
    return {
        "order_id": os.environ.get("TEST_ORDER_ID", "4321"),
        "customer_email": os.environ.get("TEST_CUSTOMER_EMAIL", "test@example.com"),
        "line_items": [
            {
                "id": 12345678,
                "title": "Test Product",
                "quantity": 1,
                "price": "25.00",
                "fulfillment_status": "fulfilled"
            }
        ]
    }

@pytest.fixture
def conversation_id():
    """Generate a unique conversation ID for each test"""
    return str(uuid.uuid4())

@pytest.fixture
def mock_shopify_order():
    """Mock Shopify order data for testing"""
    return {
        "id": 4321,
        "order_number": "4321",
        "email": "test@example.com",
        "created_at": "2024-01-15T10:00:00Z",
        "financial_status": "paid",
        "fulfillment_status": "fulfilled",
        "total_price": "25.00",
        "currency": "USD",
        "line_items": [
            {
                "id": 12345678,
                "title": "Classic T-Shirt",
                "quantity": 1,
                "price": "25.00",
                "product_id": 98765,
                "variant_id": 123456,
                "fulfillment_status": "fulfilled",
                "fulfillable_quantity": 0,
                "returned_quantity": 0
            }
        ],
        "customer": {
            "id": 555666,
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "Customer"
        },
        "shipping_address": {
            "first_name": "Test",
            "last_name": "Customer",
            "address1": "123 Test St",
            "city": "Test City",
            "province": "NY",
            "country": "United States",
            "zip": "12345"
        }
    }

@pytest.fixture(scope="session")
def test_config():
    """Configuration for integration tests"""
    return {
        "timeout": 30,  # seconds
        "max_retries": 3,
        "retry_delay": 1.0,  # seconds
        "performance_thresholds": {
            "response_time_avg": 2.0,  # seconds
            "response_time_p95": 5.0,  # seconds
            "success_rate_min": 95.0,  # percentage
            "concurrent_users_max": 10
        }
    }

@pytest.fixture
def api_client(api_base_url, test_headers):
    """Return a configured API client for making requests"""
    class APIClient:
        def __init__(self, base_url, headers):
            self.base_url = base_url
            self.headers = headers
            self.session = requests.Session()
            self.session.headers.update(headers)
        
        def get(self, endpoint, **kwargs):
            url = f"{self.base_url}{endpoint}"
            return self.session.get(url, **kwargs)
        
        def post(self, endpoint, **kwargs):
            url = f"{self.base_url}{endpoint}"
            return self.session.post(url, **kwargs)
        
        def put(self, endpoint, **kwargs):
            url = f"{self.base_url}{endpoint}"
            return self.session.put(url, **kwargs)
        
        def delete(self, endpoint, **kwargs):
            url = f"{self.base_url}{endpoint}"
            return self.session.delete(url, **kwargs)
    
    return APIClient(api_base_url, test_headers)

def wait_for_api_ready(api_base_url, timeout=60):
    """Wait for the API to be ready"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{api_base_url}/health", timeout=5)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(2)
    return False

@pytest.fixture(scope="session", autouse=True)
def ensure_api_ready(api_base_url):
    """Ensure the API is ready before running tests"""
    if not wait_for_api_ready(api_base_url):
        pytest.skip("API is not ready for testing")

@pytest.fixture
def performance_tracker():
    """Track performance metrics during tests"""
    class PerformanceTracker:
        def __init__(self):
            self.metrics = []
        
        def record_request(self, start_time, end_time, status_code, endpoint):
            """Record a request's performance metrics"""
            self.metrics.append({
                "start_time": start_time,
                "end_time": end_time,
                "duration": end_time - start_time,
                "status_code": status_code,
                "endpoint": endpoint,
                "success": 200 <= status_code < 300
            })
        
        def get_stats(self):
            """Get performance statistics"""
            if not self.metrics:
                return {}
            
            durations = [m["duration"] for m in self.metrics]
            successes = [m for m in self.metrics if m["success"]]
            
            return {
                "total_requests": len(self.metrics),
                "successful_requests": len(successes),
                "success_rate": len(successes) / len(self.metrics) * 100,
                "avg_duration": sum(durations) / len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
                "p95_duration": sorted(durations)[int(len(durations) * 0.95)]
            }
    
    return PerformanceTracker() 