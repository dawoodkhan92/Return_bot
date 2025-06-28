#!/usr/bin/env python3
"""
Simple test runner for Shopify Returns Agency

This script runs basic tests for all modules to ensure they work correctly.
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

def run_basic_tests():
    """Run basic functionality tests for all components"""
    print("=" * 60)
    print("SHOPIFY RETURNS AGENCY - BASIC TESTS")
    print("=" * 60)
    
    # Test PolicyChecker
    print("\n1. Testing PolicyChecker...")
    try:
        from tools.policy_checker import PolicyChecker
        from datetime import datetime, timedelta
        
        pc = PolicyChecker()
        
        # Test valid case
        valid_result = pc.check_policy(
            order_date=(datetime.now() - timedelta(days=10)).isoformat(),
            item_id="test_123",
            return_reason="defective"
        )
        assert valid_result['decision'] == 'approve'
        print("   ✓ PolicyChecker working correctly")
        
    except Exception as e:
        print(f"   ✗ PolicyChecker failed: {e}")
        return False
    
    # Test ActionLogger
    print("\n2. Testing ActionLogger...")
    try:
        from tools.action_logger import ActionLogger
        import tempfile
        
        temp_log = os.path.join(tempfile.gettempdir(), 'test_actions.log')
        logger = ActionLogger(log_file_path=temp_log)
        
        result = logger.log_action("test_001", "approve", "Test logging")
        assert "Successfully logged" in result
        print("   ✓ ActionLogger working correctly")
        
        # Clean up
        try:
            if os.path.exists(temp_log):
                os.remove(temp_log)
        except PermissionError:
            pass  # File might be locked, ignore
            
    except Exception as e:
        print(f"   ✗ ActionLogger failed: {e}")
        return False
    
    # Test RefundProcessor
    print("\n3. Testing RefundProcessor...")
    try:
        from tools.refund_processor import RefundProcessor
        import tempfile
        
        temp_log = os.path.join(tempfile.gettempdir(), 'test_refunds.log')
        processor = RefundProcessor(log_file_path=temp_log)
        
        result = processor.process_refund("order_123", 50.0, "approve")
        assert "approved and logged" in result
        print("   ✓ RefundProcessor working correctly")
        
        # Clean up
        try:
            if os.path.exists(temp_log):
                os.remove(temp_log)
        except PermissionError:
            pass  # File might be locked, ignore
            
    except Exception as e:
        print(f"   ✗ RefundProcessor failed: {e}")
        return False
    
    # Test ReturnsAgent
    print("\n4. Testing ReturnsAgent...")
    try:
        from agents.returns_agent import ReturnsAgent
        from datetime import datetime, timedelta
        import tempfile
        
        temp_log = os.path.join(tempfile.gettempdir(), 'test_agent.log')
        agent = ReturnsAgent(log_file_path=temp_log)
        
        # Test webhook processing
        webhook_data = {
            'id': 'test_webhook',
            'order_id': 'order_123',
            'amount': 49.99,
            'created_at': (datetime.now() - timedelta(days=10)).isoformat(),
            'line_items': [{'id': 'item_123'}],
            'reason': 'defective',
            'email': 'customer@example.com'
        }
        
        result = agent.process_refund_webhook(webhook_data)
        assert result['status'] == 'success'
        assert result['decision'] == 'approve'
        print("   ✓ ReturnsAgent working correctly")
        
        # Clean up log files
        log_dir = os.path.dirname(temp_log)
        for file in os.listdir(log_dir):
            if file.startswith('test_'):
                try:
                    os.remove(os.path.join(log_dir, file))
                except:
                    pass
            
    except Exception as e:
        print(f"   ✗ ReturnsAgent failed: {e}")
        return False
    
    # Test Flask app imports
    print("\n5. Testing Flask App...")
    try:
        from app import create_app
        app = create_app()
        assert app is not None
        print("   ✓ Flask App working correctly")
        
    except Exception as e:
        print(f"   ✗ Flask App failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED! Your Shopify Returns Agency is ready!")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    success = run_basic_tests()
    if not success:
        sys.exit(1)
    else:
        print("\n💡 Next steps:")
        print("   1. Set up your .env file with configuration")
        print("   2. Install dependencies: pip install -r requirements.txt")
        print("   3. Run the Flask app: python app.py")
        print("   4. Test the webhook endpoint!") 