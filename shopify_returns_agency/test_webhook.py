#!/usr/bin/env python3
"""
Comprehensive test for Shopify Returns Agent

This script simulates Shopify webhook requests to test the agent's functionality.
Run this to verify your agent is working correctly with different scenarios.
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from agents.returns_agent import ReturnsAgent

def create_sample_webhook(scenario: str) -> dict:
    """Create sample webhook data for different test scenarios"""
    
    base_webhook = {
        'id': f'webhook_{scenario}',
        'order_id': f'order_{scenario}',
        'line_items': [{'id': f'item_{scenario}'}],
        'email': f'customer_{scenario}@example.com'
    }
    
    if scenario == 'approve':
        # Recent order with valid return reason - should APPROVE
        return {
            **base_webhook,
            'amount': 49.99,
            'created_at': (datetime.now() - timedelta(days=10)).isoformat(),
            'reason': 'defective'
        }
    
    elif scenario == 'deny_expired':
        # Old order outside return window - should DENY
        return {
            **base_webhook,
            'amount': 75.00,
            'created_at': (datetime.now() - timedelta(days=40)).isoformat(),
            'reason': 'defective'
        }
    
    elif scenario == 'flag_invalid_reason':
        # Recent order with invalid return reason - should FLAG
        return {
            **base_webhook,
            'amount': 29.99,
            'created_at': (datetime.now() - timedelta(days=5)).isoformat(),
            'reason': 'I_changed_my_mind_but_this_is_not_valid'
        }
    
    elif scenario == 'edge_case_missing_data':
        # Webhook with missing data - should handle gracefully
        return {
            'id': 'webhook_incomplete',
            # Missing most required fields
            'amount': 'invalid_amount'
        }
    
    else:
        # Default case
        return {
            **base_webhook,
            'amount': 35.50,
            'created_at': (datetime.now() - timedelta(days=15)).isoformat(),
            'reason': 'wrong_size'
        }

def run_webhook_tests():
    """Run comprehensive webhook tests"""
    print("=" * 70)
    print("🛍️  SHOPIFY RETURNS AGENT - WEBHOOK TESTING")
    print("=" * 70)
    
    # Initialize agent
    import tempfile
    temp_log = os.path.join(tempfile.gettempdir(), 'webhook_test.log')
    agent = ReturnsAgent(return_window_days=30, log_file_path=temp_log)
    
    test_scenarios = [
        ('approve', 'Recent order with defective item'),
        ('deny_expired', 'Order outside 30-day return window'),
        ('flag_invalid_reason', 'Recent order with invalid return reason'),
        ('edge_case_missing_data', 'Webhook with incomplete data'),
        ('default', 'Standard valid return request')
    ]
    
    results = []
    
    print(f"\nRunning {len(test_scenarios)} test scenarios...\n")
    
    for scenario, description in test_scenarios:
        print(f"📋 Test: {scenario.upper()}")
        print(f"   Description: {description}")
        
        # Create webhook data
        webhook_data = create_sample_webhook(scenario)
        
        # Process webhook
        result = agent.process_refund_webhook(webhook_data)
        
        # Display results
        status = result.get('status', 'unknown')
        decision = result.get('decision', 'unknown')
        reason = result.get('reason', 'No reason provided')
        
        print(f"   📊 Result: {decision.upper()} ({status})")
        print(f"   💬 Reason: {reason}")
        
        if result.get('event_id'):
            print(f"   🔍 Event ID: {result['event_id']}")
        
        results.append({
            'scenario': scenario,
            'decision': decision,
            'status': status,
            'webhook_data': webhook_data,
            'result': result
        })
        
        print("   " + "-" * 50)
    
    # Summary
    print("\n" + "=" * 70)
    print("📈 TEST SUMMARY")
    print("=" * 70)
    
    decision_counts = {}
    for result in results:
        decision = result['decision']
        decision_counts[decision] = decision_counts.get(decision, 0) + 1
    
    print(f"Total tests run: {len(results)}")
    for decision, count in decision_counts.items():
        print(f"  • {decision.upper()}: {count}")
    
    # Expected results verification
    expected_decisions = {
        'approve': 'approve',
        'deny_expired': 'deny', 
        'flag_invalid_reason': 'flag',
        'edge_case_missing_data': 'error',  # Might be error due to invalid data
        'default': 'approve'
    }
    
    print("\n🔍 VERIFICATION:")
    all_passed = True
    for result in results:
        scenario = result['scenario']
        actual = result['decision']
        expected = expected_decisions.get(scenario, 'unknown')
        
        # For edge case, allow either 'error' status or 'deny'/'flag' decision
        if scenario == 'edge_case_missing_data':
            passed = result['status'] == 'error' or actual in ['deny', 'flag']
        else:
            passed = actual == expected
        
        status_icon = "✅" if passed else "❌"
        print(f"  {status_icon} {scenario}: Expected {expected}, Got {actual}")
        
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Your agent is working correctly!")
        print("\n📋 Your webhook endpoint is ready to receive:")
        print(f"   • URL: https://returns-agent-dev.ngrok.io/shopify/returns-webhook")
        print("   • Method: POST")
        print("   • Expected decisions: approve, deny, flag")
    else:
        print("\n⚠️  Some tests failed. Please review the agent logic.")
    
    # Clean up
    try:
        if os.path.exists(temp_log):
            os.remove(temp_log)
    except:
        pass
    
    return results

def test_direct_webhook_call():
    """Test the webhook endpoint directly (requires Flask app to be running)"""
    print("\n" + "=" * 70)
    print("🌐 DIRECT WEBHOOK ENDPOINT TEST")
    print("=" * 70)
    
    try:
        import requests
        webhook_url = "https://returns-agent-dev.ngrok.io/shopify/returns-webhook"
        
        # Test webhook data
        test_webhook = create_sample_webhook('approve')
        
        print(f"Sending POST request to: {webhook_url}")
        print(f"Payload: {json.dumps(test_webhook, indent=2)}")
        
        response = requests.post(webhook_url, json=test_webhook, timeout=10)
        
        print(f"\n📡 Response Status: {response.status_code}")
        print(f"📄 Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook endpoint is working!")
        else:
            print("❌ Webhook endpoint returned an error")
            
    except ImportError:
        print("⚠️  requests library not installed. Install with: pip install requests")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to webhook endpoint.")
        print("   Make sure your Flask app is running and ngrok tunnel is active:")
        print("   1. Run: python app.py")
        print("   2. Run: ngrok http 5000")
        print("   3. Update webhook URL in config if needed")
    except Exception as e:
        print(f"❌ Error testing webhook: {str(e)}")

if __name__ == '__main__':
    print("Starting Shopify Returns Agent tests...\n")
    
    # Run agent logic tests
    results = run_webhook_tests()
    
    # Ask if user wants to test the webhook endpoint
    print("\n" + "=" * 70)
    try:
        test_endpoint = input("Do you want to test the webhook endpoint directly? (y/n): ").lower().strip()
        if test_endpoint == 'y':
            test_direct_webhook_call()
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    
    print("\n🏁 Testing complete!")
    print("\n💡 Next steps:")
    print("   1. Set up your .env file with Shopify webhook secret")
    print("   2. Install dependencies: pip install -r requirements.txt") 
    print("   3. Run the Flask app: python app.py")
    print("   4. Set up ngrok tunnel: ngrok http 5000")
    print("   5. Configure Shopify webhook URL")
    print("   6. Test with real Shopify webhooks!") 