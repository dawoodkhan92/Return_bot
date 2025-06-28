#!/usr/bin/env python3
"""
Test script for webhook validation functionality.
"""

import json
import hmac
import hashlib
import base64
import sys
import os
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, verify_shopify_webhook

def generate_shopify_hmac(data, secret):
    """Generate HMAC signature like Shopify does"""
    return base64.b64encode(
        hmac.new(
            secret.encode('utf-8'),
            data.encode('utf-8') if isinstance(data, str) else data,
            hashlib.sha256
        ).digest()
    ).decode('utf-8')

def get_test_webhook_data():
    """Generate realistic test webhook data"""
    recent_date = (datetime.now() - timedelta(days=10)).isoformat()
    return {
        "id": "webhook_test_123",
        "order_id": "order_12345",
        "amount": 25.99,
        "created_at": recent_date,
        "line_items": [{"id": "item_456", "product_id": "prod_789"}],
        "reason": "defective",
        "email": "customer@test.com",
        "refund_line_items": [
            {
                "id": "refund_item_123",
                "line_item_id": "item_456",
                "quantity": 1
            }
        ]
    }

def test_webhook_validation():
    """Test the webhook validation functionality"""
    print("Testing Shopify webhook validation...")
    
    # Test data
    test_secret = "test_webhook_secret"
    test_payload = '{"order_id": "12345", "amount": 50.00}'
    test_payload_bytes = test_payload.encode('utf-8')
    
    # Generate valid HMAC
    valid_hmac = generate_shopify_hmac(test_payload_bytes, test_secret)
    print(f"Generated HMAC: {valid_hmac}")
    
    # Test 1: Valid HMAC should pass
    result = verify_shopify_webhook(test_payload_bytes, valid_hmac, test_secret)
    print(f"Test 1 - Valid HMAC: {'PASS' if result else 'FAIL'}")
    assert result, "Valid HMAC should pass verification"
    
    # Test 2: Invalid HMAC should fail
    invalid_hmac = "invalid_hmac_signature"
    result = verify_shopify_webhook(test_payload_bytes, invalid_hmac, test_secret)
    print(f"Test 2 - Invalid HMAC: {'PASS' if not result else 'FAIL'}")
    assert not result, "Invalid HMAC should fail verification"
    
    # Test 3: Missing HMAC should fail
    result = verify_shopify_webhook(test_payload_bytes, None, test_secret)
    print(f"Test 3 - Missing HMAC: {'PASS' if not result else 'FAIL'}")
    assert not result, "Missing HMAC should fail verification"
    
    # Test 4: Missing secret should fail
    result = verify_shopify_webhook(test_payload_bytes, valid_hmac, None)
    print(f"Test 4 - Missing secret: {'PASS' if not result else 'FAIL'}")
    assert not result, "Missing secret should fail verification"
    
    print("All webhook validation tests passed!")

def test_flask_app_with_validation():
    """Test the Flask app with webhook validation"""
    print("\nTesting Flask app with webhook validation...")
    
    # Set up test environment BEFORE creating the app
    os.environ['SHOPIFY_WEBHOOK_SECRET'] = 'test_webhook_secret'
    os.environ['FLASK_ENV'] = 'testing'
    
    # Import config to verify it's picking up the environment variable
    from config import config
    test_config = config['testing']()
    print(f"Config webhook secret: {test_config.SHOPIFY_WEBHOOK_SECRET}")
    
    app = create_app('testing')
    print(f"App config webhook secret: {app.config.get('SHOPIFY_WEBHOOK_SECRET')}")
    
    with app.test_client() as client:
        # Test health endpoint
        response = client.get('/health')
        assert response.status_code == 200
        print("Health endpoint test: PASS")
        
        # Get realistic test data
        test_data = get_test_webhook_data()
        test_payload = json.dumps(test_data)
        
        # Test webhook endpoint without HMAC (should fail if secret is configured)
        print("\nTesting webhook without HMAC...")
        response = client.post('/shopify/returns-webhook',
                             data=test_payload,
                             content_type='application/json')
        print(f"Webhook without HMAC: {response.status_code} (expected 401)")
        if response.status_code != 401:
            print(f"Response: {response.get_json()}")
        
        # Test webhook endpoint with valid HMAC
        print("\nTesting webhook with valid HMAC...")
        valid_hmac = generate_shopify_hmac(test_payload, 'test_webhook_secret')
        print(f"Generated valid HMAC: {valid_hmac}")
        
        response = client.post('/shopify/returns-webhook',
                             data=test_payload,
                             content_type='application/json',
                             headers={'X-Shopify-Hmac-SHA256': valid_hmac})
        print(f"Webhook with valid HMAC: {response.status_code} (expected 200)")
        if response.status_code == 200:
            result = response.get_json()
            print(f"  Decision: {result.get('decision', 'unknown')}")
        
        # Test webhook endpoint with invalid HMAC
        print("\nTesting webhook with invalid HMAC...")
        response = client.post('/shopify/returns-webhook',
                             data=test_payload,
                             content_type='application/json',
                             headers={'X-Shopify-Hmac-SHA256': 'invalid_hmac'})
        print(f"Webhook with invalid HMAC: {response.status_code} (expected 401)")
        if response.status_code != 401:
            print(f"Response: {response.get_json()}")
            # This should fail the test
            assert False, f"Expected 401 but got {response.status_code}"
    
    print("Flask app webhook validation tests completed!")

def test_without_secret():
    """Test the Flask app without webhook secret (should skip validation)"""
    print("\nTesting Flask app without webhook secret...")
    
    # Remove webhook secret
    if 'SHOPIFY_WEBHOOK_SECRET' in os.environ:
        del os.environ['SHOPIFY_WEBHOOK_SECRET']
    os.environ['FLASK_ENV'] = 'testing'
    
    app = create_app('testing')
    print(f"App config webhook secret (should be None): {app.config.get('SHOPIFY_WEBHOOK_SECRET')}")
    
    with app.test_client() as client:
        test_data = get_test_webhook_data()
        test_payload = json.dumps(test_data)
        
        # Test webhook endpoint without secret configured (should work)
        response = client.post('/shopify/returns-webhook',
                             data=test_payload,
                             content_type='application/json')
        print(f"Webhook without secret configured: {response.status_code} (expected 200)")
        if response.status_code == 200:
            result = response.get_json()
            print(f"  Decision: {result.get('decision', 'unknown')}")
    
    print("No secret test completed!")

if __name__ == '__main__':
    try:
        test_webhook_validation()
        test_flask_app_with_validation()
        test_without_secret()
        print("\n✅ All webhook validation tests passed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 